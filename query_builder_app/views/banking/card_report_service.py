# query_builder_app/views/banking/card_report_service.py


import os
import psycopg2
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import base64
import csv
import tempfile
import zipfile
from datetime import datetime

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

def compress_files(directory_name):
    """Compress all CSV files in the directory into a single zip file."""
    zip_file_path = os.path.join(directory_name, f"{directory_name}.zip")
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(directory_name):
            for file in files:
                if file.endswith('.csv'):
                    zipf.write(os.path.join(root, file), arcname=file)
    return zip_file_path

def generate_csv_card_report():
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp(prefix='card_report_')
    csv_file_path = os.path.join(temp_dir, 'card_report.csv')

    # Get data from banking_relations database
    conn_banking = create_db_connection(db_config_banking_relations)
    cursor_banking = conn_banking.cursor()
    banking_data, banking_columns = execute_query(cursor_banking, query_banking_relations)

    # Get data from platform database
    conn_platform = create_db_connection(db_config_platform)
    cursor_platform = conn_platform.cursor()
    platform_data, platform_columns = execute_query(cursor_platform, query_platform)

    # Create a dictionary to store platform data keyed by user_id
    platform_dict = {row[0]: row for row in platform_data}

    # Combine data and write to CSV
    with open(csv_file_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        
        # Write header
        header = banking_columns + [col for col in platform_columns if col != 'user_id']
        csvwriter.writerow(header)

        # Write data rows
        for row_num, banking_row in enumerate(banking_data, start=1):
            user_id = banking_row[2]  # Assuming user_id is at index 2 in banking_relations
            platform_row = platform_dict.get(user_id)
            
            if platform_row:
                combined_row = list(banking_row)
                for i, value in enumerate(platform_row[1:], start=len(banking_columns)):
                    column_name = platform_columns[i]
                    if column_name.startswith('_'):
                        decrypted_value = decrypt_value(value, row_num, column_name)
                        combined_row.append(decrypted_value)
                    else:
                        combined_row.append(value)
                
                csvwriter.writerow(combined_row)

    # Close database connections
    cursor_banking.close()
    conn_banking.close()
    cursor_platform.close()
    conn_platform.close()

    # Compress the CSV file
    zip_file_path = compress_files(temp_dir)

    # Remove the temporary CSV file
    os.remove(csv_file_path)

    return zip_file_path