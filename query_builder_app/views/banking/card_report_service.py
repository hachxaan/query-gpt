# query_builder_app/views/banking/card_report_service.py

import os
import psycopg2
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import base64
import csv
from datetime import datetime
import logging
import tempfile
import requests

logger = logging.getLogger(__name__)

# Load environment variables from the .env file
load_dotenv()

# API configuration for Solid Report
SOLID_REPORT_API_KEY = os.getenv('SOLID_REPORT_API_KEY')
SOLID_REPORT_API_URL = 'https://api.accesswages.com/api/v2/solid-reports/card-data'

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

def get_solid_report_data():
    """Fetch data from Solid Report API."""
    headers = {
        'Content-Type': 'application/json',
        'Authorization': SOLID_REPORT_API_KEY
    }
    response = requests.get(SOLID_REPORT_API_URL, headers=headers)
    response.raise_for_status()
    return response.json()

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
        # Get data from Solid Report API
        logger.info("Fetching data from Solid Report API...")
        solid_report_data = get_solid_report_data()
        logger.info(f"Retrieved {len(solid_report_data)} records from Solid Report API")

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
            header = list(solid_report_data[0].keys()) + [col for col in platform_columns if col != 'user_id']
            csvwriter.writerow(header)
            logger.info(f"CSV header written: {', '.join(header)}")

            # Write data rows
            for row_num, solid_row in enumerate(solid_report_data, start=1):
                try:
                    user_id = solid_row.get('userId')  # Assuming userId is the key in Solid Report data
                    platform_row = platform_dict.get(user_id)
                    
                    if platform_row:
                        combined_row = list(solid_row.values())
                        for i, value in enumerate(platform_row[1:]):
                            if i + len(solid_row) < len(header):
                                column_name = header[i + len(solid_row)]
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

# The query_platform remains the same as before
query_platform = """
    SELECT 
    c.id,
    c.name,
    c.url,
    c.tier,
    c.active,
    c.created,
    c.payroll_active,
    c.peo_company,
    c.peo_company_id,
    c.updated,
    c._logo_name,
    c.licensing_fee,
    c.unique_provider_id,
    c.white_label,
    c.worked_hours,
    c.external_id,
    c.white_label_tag,
    c.time_clock,
    c.hourly_limit_wa,
    c.timecard_connection_id,
    c.pct_hours,
    c.white_label_description,
    c.has_normal_hours,
    c.wage_pct_max_custom,
    c.banking,
    c.go_live_date,
    c.mailing_group,
    c._flags,
    peo.id AS peo_company_id,
    peo.name AS peo_company_name,
    peo.url AS peo_company_url,
    peo.tier AS peo_company_tier,
    peo.active AS peo_company_active,
    peo.created AS peo_company_created,
    peo.payroll_active AS peo_company_payroll_active,
    peo.peo_company AS peo_company_peo_company,
    peo.updated AS peo_company_updated,
    peo._logo_name AS peo_company__logo_name,
    peo.licensing_fee AS peo_company_licensing_fee,
    peo.unique_provider_id AS peo_company_unique_provider_id,
    peo.white_label AS peo_company_white_label,
    peo.worked_hours AS peo_company_worked_hours,
    peo.external_id AS peo_company_external_id,
    peo.white_label_tag AS peo_company_white_label_tag,
    peo.time_clock AS peo_company_time_clock,
    peo.hourly_limit_wa AS peo_company_hourly_limit_wa,
    peo.timecard_connection_id AS peo_company_timecard_connection_id,
    peo.pct_hours AS peo_company_pct_hours,
    peo.white_label_description AS peo_company_white_label_description,
    peo.has_normal_hours AS peo_company_has_normal_hours,
    peo.wage_pct_max_custom AS peo_company_wage_pct_max_custom,
    peo.banking AS peo_company_banking,
    peo.go_live_date AS peo_company_go_live_date,
    peo.mailing_group AS peo_company_mailing_group,
    peo._flags AS peo_company__flags,
    (SELECT COUNT(*) FROM users u WHERE u.company_id = c.id AND u.inactive = FALSE) AS "active_employee",
    (SELECT COUNT(*) FROM users u WHERE u.company_id = c.id AND u.inactive = FALSE AND u.signup_date IS NULL ) AS "not_signup_employee",
    (SELECT COUNT(*) FROM users u WHERE u.company_id = c.id AND u.inactive = FALSE AND u.signup_date IS NOT NULL ) AS "signup_employee"
FROM 
    companies c
LEFT JOIN 
    companies peo ON c.peo_company_id = peo.id
"""