


import os
import csv
import psycopg2
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import base64

# Load environment variables from the .env file
load_dotenv()

# Database configuration for banking relations
db_config_banking_relations = {
    'user': os.getenv('USER_BANKING_RELATIONS'),
    'password': os.getenv('PASSWORD_BANKING_RELATIONS'),
    'dbname': os.getenv('NAME_BANKING_RELATIONS'),
    'host': os.getenv('HOST_BANKING_RELATIONS'),
    'port': os.getenv('PORT_BANKING_RELATIONS')
}

# Database configuration for platform
db_config_platform = {
    'user': os.getenv('USER_PLATFORM'),
    'password': os.getenv('PASSWORD_PLATFORM'),
    'dbname': os.getenv('NAME_PLATFORM'),
    'host': os.getenv('HOST_PLATFORM'),
    'port': os.getenv('PORT_PLATFORM')
}


DB_KEY = os.getenv('DB_KEY')


class FernetSingleton:
    """Singleton class for Fernet decryption."""
    
    class __FernetSingleton:
        def __init__(self):
            key_bytes = DB_KEY.encode('utf-8')
            self.fernet = Fernet(key_bytes)
    
    instance = None

    def __init__(self):
        if not FernetSingleton.instance:
            FernetSingleton.instance = FernetSingleton.__FernetSingleton().fernet

    def __getattr__(self, name):
        return getattr(self.instance, name)

# Initialize Fernet singleton
fernet = FernetSingleton()

def create_db_connection(db_config):
    """Create and return a database connection."""
    return psycopg2.connect(
        dbname=db_config['dbname'],
        user=db_config['user'],
        password=db_config['password'],
        host=db_config['host'],
        port=db_config['port']
    )

def execute_query(cursor, query):
    """Execute the given SQL query and return the results."""
    cursor.execute(query)
    return cursor.fetchall(), [desc[0] for desc in cursor.description]

def decrypt_value(value, row_number, field_name):
    """Decrypt a base64 encoded value using Fernet."""
    try:
        if isinstance(value, memoryview):
            value = value.tobytes()
        if isinstance(value, bytes):
            return fernet.decrypt(value).decode("utf-8")
        elif isinstance(value, str):
            value_bytes = base64.urlsafe_b64decode(value)
            return fernet.decrypt(value_bytes).decode("utf-8")
        else:
            raise ValueError("Unsupported value type for decryption")
    except Exception as e:
        print(f"Error decrypting {field_name} in row {row_number}: {e}")
        return None



def generate_csv_card_report():
    """Main function to get the card report from database records and return the csv"""
    query_banking_relations = """
        SELECT id, 
            customer_id, 
            user_id, 
            peo_company_id, 
            company_id, 
            white_label, 
            person_id,
            account_id, 
            card_id, 
            card_pan, 
            card_bin, 
            card_created_at, 
            card_card_type, 
            card_card_status, 
            "createdPersonId", 
            created_at
        FROM cards_program
        WHERE user_id IS NOT NULL
        order user_id;
    """

    query_platform = """
        SELECT 
            u.id AS user_id,
            u.first_name AS first_name,
            u.cashback_balance AS cashback_balance,
            u.cashback_updated AS cashback_updated,
            u.registration_date AS registration_date,
            u.inactive AS inactive,
            u.city AS city,
            u.state AS state,
            u.zip_code AS zip_code,
            u.terms_conditions AS terms_conditions,
            u.promotional_sms AS promotional_sms,
            u.promotional_email AS promotional_email,
            u.last_login_date AS last_login_date,
            u.confirmed_email AS confirmed_email,
            u.admin_company AS admin_company,
            u.admin_multikrd AS admin_multikrd,
            u.admin_peo AS admin_peo,
            u.payroll_active AS payroll_active,
            u.payroll_last_date AS payroll_last_date,
            u.payroll_type AS payroll_type,
            u.promotional_phone_calls AS promotional_phone_calls,
            u.onboarding AS onboarding,
            u.cashback_historic AS cashback_historic,
            u.cashback_pending AS cashback_pending,
            u.wage_access_program AS wage_access_program,
            u.payroll_frequency AS payroll_frequency,
            u.worked_hours AS worked_hours,
            u.termination_date AS termination_date,
            u.signup_date AS signup_date,
            u.direct_deposit AS direct_deposit,
            u._email AS _email,
            u._last_name AS _last_name,
            u._birthdate AS _birthdate,
            u._mobile_phone AS _mobile_phone,
            u._payroll_daily AS _payroll_daily,
            u._payroll_hourly AS _payroll_hourly,
            u._payroll_salary AS _payroll_salary,
            u.customer_uuid AS customer_uuid,
            c.name AS company_name,
            c.active AS company_active,
            c.created AS company_created,
            c.payroll_active AS company_payroll_active,
            c.peo_company AS company_peo_company,
            c.peo_company_id AS company_peo_company_id,
            c.white_label AS company_white_label,
            c.worked_hours AS company_worked_hours,
            c.white_label_tag AS company_white_label_tag,
            c.time_clock AS company_time_clock,
            c.hourly_limit_wa AS company_hourly_limit_wa,
            c.pct_hours AS company_pct_hours,
            c.has_normal_hours AS company_has_normal_hours,
            c.wage_pct_max_custom AS company_wage_pct_max_custom,
            c.banking AS company_banking,
            c.go_live_date AS company_go_live_date,
            c.mailing_group AS company_mailing_group
        FROM users u, companies c
        WHERE u.customer_uuid IS NOT NULL
           AND u.company_id = c.id
        ORDER BY u.user_id;
    """
