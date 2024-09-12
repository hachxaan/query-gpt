import os
import psycopg2
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import base64
import csv
from datetime import datetime
import logging
import tempfile

logger = logging.getLogger(__name__)

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
    logger.info(f"Connecting to database: {db_config['dbname']} on {db_config['host']}:{db_config['port']}")
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
        if value is None:
            return None
        if isinstance(value, memoryview):
            value = value.tobytes()
        if isinstance(value, bytes):
            return fernet.decrypt(value).decode("utf-8")
        elif isinstance(value, str):
            value_bytes = base64.urlsafe_b64decode(value)
            return fernet.decrypt(value_bytes).decode("utf-8")
        else:
            logger.warning(f"Unsupported value type for decryption in {field_name}, row {row_number}: {type(value)}")
            return str(value)
    except Exception as e:
        logger.error(f"Error decrypting {field_name} in row {row_number}: {e}")
        return str(value)

def generate_csv_card_report():
    temp_dir = '/home/administrador/temp-files'
    if not os.access(temp_dir, os.W_OK):
        logger.warning(f"No write access to {temp_dir}. Using system temp directory.")
        temp_dir = tempfile.gettempdir()
    
    os.makedirs(temp_dir, exist_ok=True)
    logger.info(f"Using directory: {temp_dir}")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_file_path = os.path.join(temp_dir, f'card_report_{timestamp}.csv')
    
    logger.info(f"CSV file path: {csv_file_path}")

    try:
        # Get data from banking_relations database
        logger.info("Connecting to banking_relations database...")
        conn_banking = create_db_connection(db_config_banking_relations)
        cursor_banking = conn_banking.cursor()
        banking_data, banking_columns = execute_query(cursor_banking, query_banking_relations)
        logger.info(f"Retrieved {len(banking_data)} records from banking_relations")

        # Get data from platform database
        logger.info("Connecting to platform database...")
        conn_platform = create_db_connection(db_config_platform)
        cursor_platform = conn_platform.cursor()
        platform_data, platform_columns = execute_query(cursor_platform, query_platform)
        logger.info(f"Retrieved {len(platform_data)} records from platform")

        # Create a dictionary to store platform data keyed by user_id
        platform_dict = {row[0]: row for row in platform_data}
        logger.info(f"Created platform dictionary with {len(platform_dict)} entries")

        # Combine data and write to CSV
        records_processed = 0
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile)
            
            # Write header
            header = banking_columns + [col for col in platform_columns if col != 'user_id']
            csvwriter.writerow(header)
            logger.info(f"CSV header written: {', '.join(header)}")

            # Write data rows
            for row_num, banking_row in enumerate(banking_data, start=1):
                try:
                    user_id = banking_row[2]  # Assuming user_id is at index 2 in banking_relations
                    platform_row = platform_dict.get(user_id)
                    
                    if platform_row:
                        combined_row = list(banking_row)
                        for i, value in enumerate(platform_row[1:]):
                            if i + len(banking_columns) < len(header):
                                column_name = header[i + len(banking_columns)]
                                if column_name.startswith('_'):
                                    decrypted_value = decrypt_value(value, row_num, column_name)
                                    combined_row.append(decrypted_value)
                                else:
                                    combined_row.append(value)
                            else:
                                logger.warning(f"Warning: Skipping extra column in platform data for row {row_num}")
                        
                        if len(combined_row) < len(header):
                            logger.warning(f"Warning: Row {row_num} has fewer columns than expected. Padding with None.")
                            combined_row.extend([None] * (len(header) - len(combined_row)))
                        
                        csvwriter.writerow(combined_row)
                        records_processed += 1
                        
                        if records_processed % 1000 == 0:
                            logger.info(f"Processed {records_processed} records")
                    else:
                        logger.warning(f"Warning: No platform data found for user_id {user_id} in row {row_num}")
                except Exception as e:
                    logger.error(f"Error processing row {row_num}: {str(e)}", exc_info=True)

        logger.info(f"Total records processed and written to CSV: {records_processed}")

        # Close database connections
        cursor_banking.close()
        conn_banking.close()
        cursor_platform.close()
        conn_platform.close()
        logger.info("Database connections closed")

        # Verify the CSV file
        if os.path.exists(csv_file_path) and os.path.getsize(csv_file_path) > 0:
            logger.info(f"CSV file verified: {csv_file_path}")
            logger.info(f"CSV file size: {os.path.getsize(csv_file_path)} bytes")
        else:
            raise FileNotFoundError(f"CSV file not created or empty: {csv_file_path}")

        return csv_file_path

    except Exception as e:
        logger.error(f"Error in generate_csv_card_report: {str(e)}", exc_info=True)
        raise

# Define the SQL queries
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
    ORDER BY user_id;
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
    ORDER BY u.id;
""" 