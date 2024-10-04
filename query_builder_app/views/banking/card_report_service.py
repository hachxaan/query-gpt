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
import logging
import requests

logger = logging.getLogger(__name__)

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
    SELECT * FROM vw_users_with_companies_full WHERE users_customer_uuid IS NOT NULL;
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

# query_builder_app/views/banking/card_report_service.py

import csv
import os
import tempfile
from datetime import datetime
import logging
import requests

logger = logging.getLogger(__name__)

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
        
        if not solid_report_data:
            logger.error("No data received from Solid Report API")
            return None

        # Log first few records from Solid Report API for debugging
        logger.debug(f"First 3 records from Solid Report API: {solid_report_data[:3]}")

        # Get data from platform database
        logger.info("Connecting to platform database...")
        conn_platform = create_db_connection(db_config_platform)
        cursor_platform = conn_platform.cursor()
        platform_data, platform_columns = execute_query(cursor_platform, query_platform)
        logger.info(f"Retrieved {len(platform_data)} records from platform")

        if not platform_data:
            logger.error("No data received from platform database")
            return None

        # Create a dictionary to store platform data keyed by user_id
        platform_dict = {str(row[0]): row for row in platform_data}
        logger.info(f"Created platform dictionary with {len(platform_dict)} entries")

        # Combine data and write to CSV
        records_processed = 0
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile, quotechar='"', quoting=csv.QUOTE_ALL)
            
            # Write header
            solid_report_headers = list(solid_report_data[0].keys())
            platform_headers = [col for col in platform_columns if col != 'user_id']
            header = solid_report_headers + platform_headers
            csvwriter.writerow(header)
            logger.info(f"CSV header written: {', '.join(header)}")

            # Write data rows
            for row_num, solid_row in enumerate(solid_report_data, start=1):
                try:
                    # Corregir el desplazamiento de datos
                    corrected_solid_row = {}
                    wallet_id_index = solid_report_headers.index('walletId')
                    for i, key in enumerate(solid_report_headers):
                        if i <= wallet_id_index:
                            corrected_solid_row[key] = solid_row.get(key, '')
                        else:
                            corrected_solid_row[key] = solid_row.get(solid_report_headers[i-1], '')
                    
                    # Obtener el user_id del campo correcto
                    user_id = str(corrected_solid_row.get('customer_userId'))
                    
                    if user_id is None or user_id == '':
                        logger.warning(f"No valid customer_userId found in Solid Report data for row {row_num}. Available fields: {', '.join(corrected_solid_row.keys())}")
                        continue

                    platform_row = platform_dict.get(user_id)
                    
                    if platform_row:
                        combined_row = [str(corrected_solid_row.get(key, '')) for key in solid_report_headers]
                        for value in platform_row[1:]:  # Excluir user_id que ya está en solid_row
                            if not isinstance(value, str) and value.startswith('_'):
                                decrypted_value = decrypt_value(value, row_num, value)
                                combined_row.append(str(decrypted_value))
                            else:
                                combined_row.append(str(value))
                        
                        csvwriter.writerow(combined_row)
                        records_processed += 1
                        
                        if records_processed % 1000 == 0:
                            logger.info(f"Processed {records_processed} records")
                    else:
                        logger.warning(f"Warning: No platform data found for customer_userId {user_id} in row {row_num}")
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
