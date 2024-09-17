# query_builder_app/views/banking/card_report_service.py

import os
import sys
import psycopg2
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import base64
import csv
from datetime import datetime
import logging
import tempfile
import requests

# Load environment variables from the .env file
load_dotenv()

# Configuración del logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stdout
)

# Forzar el vaciado del buffer después de cada mensaje
class RealTimeHandler(logging.StreamHandler):
    def emit(self, record):
        super().emit(record)
        self.flush()

logger = logging.getLogger(__name__)
logger.addHandler(RealTimeHandler(sys.stdout))

# The query_platform now uses the new view
query_platform = """
    SELECT * FROM vw_users_with_companies_full_v1 WHERE users_customer_uuid IS NOT NULL;
"""

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
    logger.info(f"Connecting to database: {db_config['dbname']} on {db_config['host']}:{db_config['port']}:{db_config['user']}")
    sys.stdout.flush()
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
            sys.stdout.flush()
            return str(value)
    except Exception as e:
        logger.error(f"Error decrypting {field_name} in row {row_number}: {e}")
        sys.stdout.flush()
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
        sys.stdout.flush()
        temp_dir = tempfile.gettempdir()
    
    os.makedirs(temp_dir, exist_ok=True)
    logger.info(f"Using directory: {temp_dir}")
    sys.stdout.flush()
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_file_path = os.path.join(temp_dir, f'card_report_{timestamp}.csv')
    
    logger.info(f"CSV file path: {csv_file_path}")
    sys.stdout.flush()

    try:
        # Get data from Solid Report API
        logger.info("Fetching data from Solid Report API...")
        sys.stdout.flush()
        solid_report_data = get_solid_report_data()
        logger.info(f"Retrieved {len(solid_report_data)} records from Solid Report API")
        sys.stdout.flush()

        # Get data from platform database
        logger.info("Connecting to platform database...")
        sys.stdout.flush()
        conn_platform = create_db_connection(db_config_platform)
        cursor_platform = conn_platform.cursor()
        platform_data, platform_columns = execute_query(cursor_platform, query_platform)
        logger.info(f"Retrieved {len(platform_data)} records from platform")
        sys.stdout.flush()

        # Create a dictionary to store platform data keyed by user_customer_uuid
        platform_dict = {row[platform_columns.index('users_customer_uuid')]: row for row in platform_data}
        logger.info(f"Created platform dictionary with {len(platform_dict)} entries")
        sys.stdout.flush()

        # Combine data and write to CSV
        records_processed = 0
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile)
            
            # Write header
            header = list(solid_report_data[0].keys()) + platform_columns
            csvwriter.writerow(header)
            logger.info(f"CSV header written: {', '.join(header)}")
            sys.stdout.flush()

            # Write data rows
            for row_num, solid_row in enumerate(solid_report_data, start=1):
                try:
                    customer_uuid = solid_row.get('customer_uuid')
                    platform_row = platform_dict.get(customer_uuid)
                    
                    if platform_row:
                        combined_row = list(solid_row.values())
                        for i, value in enumerate(platform_row):
                            column_name = platform_columns[i]
                            if column_name.startswith('users__') or column_name.startswith('companies__') or column_name.startswith('peo_company__'):
                                decrypted_value = decrypt_value(value, row_num, column_name)
                                combined_row.append(decrypted_value)
                            else:
                                combined_row.append(value)
                        
                        if len(combined_row) < len(header):
                            logger.warning(f"Warning: Row {row_num} has fewer columns than expected. Padding with None.")
                            sys.stdout.flush()
                            combined_row.extend([None] * (len(header) - len(combined_row)))
                        
                        csvwriter.writerow(combined_row)
                        records_processed += 1
                        
                        if records_processed % 1000 == 0:
                            logger.info(f"Processed {records_processed} records")
                            sys.stdout.flush()
                    else:
                        logger.warning(f"Warning: No platform data found for customer_uuid {customer_uuid} in row {row_num}")
                        sys.stdout.flush()
                except Exception as e:
                    logger.error(f"Error processing row {row_num}: {str(e)}", exc_info=True)
                    sys.stdout.flush()

        logger.info(f"Total records processed and written to CSV: {records_processed}")
        sys.stdout.flush()

        # Close database connections
        cursor_platform.close()
        conn_platform.close()
        logger.info("Database connections closed")
        sys.stdout.flush()

        # Verify the CSV file
        if os.path.exists(csv_file_path) and os.path.getsize(csv_file_path) > 0:
            logger.info(f"CSV file verified: {csv_file_path}")
            logger.info(f"CSV file size: {os.path.getsize(csv_file_path)} bytes")
            sys.stdout.flush()
        else:
            raise FileNotFoundError(f"CSV file not created or empty: {csv_file_path}")

        return csv_file_path

    except Exception as e:
        logger.error(f"Error in generate_csv_card_report: {str(e)}", exc_info=True)
        sys.stdout.flush()
        raise