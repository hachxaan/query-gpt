import os
import csv
import psycopg2
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import base64
import zipfile
import re
import logging
import uuid

# Load environment variables from the .env file
load_dotenv()

logger = logging.getLogger(__name__)

# Database configuration
DB_USER = os.getenv('POSTGRES_USER')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')
DB_NAME = os.getenv('POSTGRES_DB')
DB_HOST = os.getenv('POSTGRES_DNS')
DB_PORT = os.getenv('POSTGRES_PORT')
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


def create_db_connection():
    """Create and return a database connection."""
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
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
        logger.error(f"Error decrypting {field_name} in row {row_number}: {e}")
        return None


def create_unique_directory(prefix):
    """Create a unique directory using UUID to avoid race conditions between concurrent requests."""
    unique_id = uuid.uuid4().hex[:8]
    directory_name = f"{prefix}_{unique_id}"
    os.makedirs(directory_name, exist_ok=True)
    return directory_name


def create_directory(directory_name):
    """Create a directory if it doesn't exist, or clear it if it does."""
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
    else:
        for file in os.listdir(directory_name):
            if file.endswith(".csv"):
                os.remove(os.path.join(directory_name, file))


def sanitize_filename(filename):
    """Sanitize the filename by removing or replacing special characters."""
    return re.sub(r'[^\w\s-]', '', filename)


def save_file(file_handle, temp_file_name, file_name_prefix, record_count, directory_name, files_generated):
    """Close file handle and rename the temporary CSV file."""
    if file_handle:
        file_handle.close()
        sanitized_file_name = sanitize_filename(file_name_prefix)
        final_file_name = os.path.join(directory_name, f"{sanitized_file_name}_{record_count}.csv")
        os.rename(temp_file_name, final_file_name)
        logger.info(f"Saved {final_file_name}")
        files_generated.append(final_file_name)


def process_rows(rows, columns, directory_name):
    """Process database rows and save them into CSV files."""
    current_file_name = ""
    csv_writer = None
    file_handle = None
    temp_file_name = None
    record_count = 0
    files_generated = []

    for row_number, row in enumerate(rows, start=1):
        logger.debug(f"Processing row {row_number} of {len(rows)}")
        email_encrypted = row[0]
        last_name_encrypted = row[1]
        email = decrypt_value(email_encrypted, row_number, "email")
        last_name = decrypt_value(last_name_encrypted, row_number, "last name")

        file_name = row[-1]

        if current_file_name != file_name:
            if csv_writer:
                save_file(file_handle, temp_file_name, file_name_prefix, record_count, directory_name, files_generated)

            current_file_name = file_name
            record_count = 0
            file_name_prefix = file_name.rsplit('_', 1)[0] if file_name else "unknown"
            sanitized_file_name_prefix = sanitize_filename(file_name_prefix)
            temp_file_name = os.path.join(directory_name, f"{sanitized_file_name_prefix}_temp.csv")
            file_handle = open(temp_file_name, mode='w', newline='', encoding='utf-8')
            csv_writer = csv.writer(file_handle)
            csv_writer.writerow(columns[:-1])  # Exclude "file_name"

        row_data = [email, last_name] + list(row[2:-1])
        csv_writer.writerow(row_data)
        record_count += 1

    if csv_writer:
        save_file(file_handle, temp_file_name, file_name_prefix, record_count, directory_name, files_generated)

    return files_generated


def save_files_list(files_generated, directory_name):
    """Save the list of generated CSV files."""
    with open(os.path.join(directory_name, 'files_generated.csv'), mode='w', newline='', encoding='utf-8') as file_list:
        csv_writer = csv.writer(file_list)
        csv_writer.writerow(['file_name'])
        for file_name in files_generated:
            csv_writer.writerow([file_name])


def compress_files(directory_name):
    """Compress all CSV files in the directory into a single zip file."""
    zip_file_path = os.path.join(directory_name, f"{os.path.basename(directory_name)}.zip")
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(directory_name):
            for file in files:
                if file.endswith('.csv'):
                    zipf.write(os.path.join(root, file), arcname=file)
    return zip_file_path


def generate_audiences_zip(query, directory_prefix):
    """Generic function to generate audience CSV files from a SQL query and return the zip path."""
    directory_name = create_unique_directory(directory_prefix)

    conn = create_db_connection()
    cursor = conn.cursor()

    try:
        rows, columns = execute_query(cursor, query)
        files_generated = process_rows(rows, columns, directory_name)
        save_files_list(files_generated, directory_name)
        zip_file_path = compress_files(directory_name)
    finally:
        cursor.close()
        conn.close()

    return zip_file_path
