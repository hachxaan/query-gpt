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

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stdout
)

class RealTimeHandler(logging.StreamHandler):
    """Forzar el vaciado del buffer después de cada mensaje."""
    def emit(self, record):
        super().emit(record)
        self.flush()

logger = logging.getLogger(__name__)
logger.addHandler(RealTimeHandler(sys.stdout))

# Consulta a la plataforma usando la nueva vista
QUERY_PLATFORM = """
    SELECT * FROM vw_users_with_companies_full_v1 WHERE users_customer_uuid IS NOT NULL;
"""

# Configuración de la API de Solid Report
SOLID_REPORT_API_KEY = os.getenv('SOLID_REPORT_API_KEY')
SOLID_REPORT_API_URL = 'https://api.accesswages.com/api/v2/solid-reports/card-data'

# Configuración de la base de datos para la plataforma
DB_CONFIG_PLATFORM = {
    'user': os.getenv('USER_PLATFORM'),
    'password': os.getenv('PASSWORD_PLATFORM'),
    'dbname': os.getenv('NAME_PLATFORM'),
    'host': os.getenv('HOST_PLATFORM'),
    'port': os.getenv('PORT_PLATFORM')
}

DB_KEY = os.getenv('DB_KEY')

class FernetSingleton:
    """Singleton para manejar la encriptación con Fernet."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            key_bytes = DB_KEY.encode('utf-8')
            cls._instance = Fernet(key_bytes)
        return cls._instance

def create_db_connection(db_config):
    """Crear y retornar la conexión a la base de datos."""
    logger.info(f"Connecting to database: {db_config['dbname']} on {db_config['host']}:{db_config['port']}")
    return psycopg2.connect(
        dbname=db_config['dbname'],
        user=db_config['user'],
        password=db_config['password'],
        host=db_config['host'],
        port=db_config['port']
    )

def execute_query(cursor, query):
    """Ejecutar la consulta SQL y retornar los resultados."""
    cursor.execute(query)
    return cursor.fetchall(), [desc[0] for desc in cursor.description]

def decrypt_value(value, row_number, field_name):
    """Desencriptar un valor codificado en base64 usando Fernet."""
    try:
        if value is None:
            return None
        if isinstance(value, memoryview):
            value = value.tobytes()
        if isinstance(value, bytes):
            return FernetSingleton().decrypt(value).decode("utf-8")
        elif isinstance(value, str):
            value_bytes = base64.urlsafe_b64decode(value)
            return FernetSingleton().decrypt(value_bytes).decode("utf-8")
        else:
            logger.warning(f"Unsupported value type for decryption in {field_name}, row {row_number}: {type(value)}")
            return str(value)
    except Exception as e:
        logger.error(f"Error decrypting {field_name} in row {row_number}: {e}")
        return str(value)

def get_solid_report_data():
    """Obtener datos de la API de Solid Report."""
    headers = {
        'Content-Type': 'application/json',
        'Authorization': SOLID_REPORT_API_KEY
    }
    response = requests.get(SOLID_REPORT_API_URL, headers=headers)
    response.raise_for_status()
    return response.json()

def write_csv_file(header, rows, csv_file_path):
    """Escribir los datos en un archivo CSV."""
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(header)  # Escribir el encabezado
        logger.info(f"CSV header written: {', '.join(header)}")
        
        for row in rows:
            csvwriter.writerow(row)

def process_data(solid_report_data, platform_data, platform_columns):
    """Combinar los datos del Solid Report y la plataforma, manejando la desencriptación."""
    platform_dict = {row[platform_columns.index('users_id')]: row for row in platform_data}
    combined_rows = []

    for row_num, solid_row in enumerate(solid_report_data, start=1):
        user_id = solid_row.get('customer_userId')
        platform_row = platform_dict.get(user_id)

        if platform_row:
            combined_row = list(solid_row.values())
            for i, value in enumerate(platform_row):
                column_name = platform_columns[i]
                if column_name.startswith(('users__', 'companies__', 'peo_company__')):
                    decrypted_value = decrypt_value(value, row_num, column_name)
                    combined_row.append(decrypted_value)
                else:
                    combined_row.append(value)

            if len(combined_row) < len(solid_row) + len(platform_columns):
                combined_row.extend([None] * ((len(solid_row) + len(platform_columns)) - len(combined_row)))

            combined_rows.append(combined_row)
        else:
            logger.warning(f"No platform data found for user_id {user_id} in row {row_num}")

    return combined_rows

def generate_csv_card_report():
    """Generar el reporte CSV combinando los datos de la API y la base de datos."""
    temp_dir = tempfile.gettempdir()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_file_path = os.path.join(temp_dir, f'card_report_{timestamp}.csv')

    try:
        # Obtener datos de la API de Solid Report
        logger.info("Fetching data from Solid Report API...")
        solid_report_data = get_solid_report_data()

        # Conectar a la base de datos y obtener datos de la plataforma
        conn_platform = create_db_connection(DB_CONFIG_PLATFORM)
        cursor_platform = conn_platform.cursor()
        platform_data, platform_columns = execute_query(cursor_platform, QUERY_PLATFORM)

        # Combinar los datos y escribirlos en el CSV
        header = list(solid_report_data[0].keys()) + platform_columns
        combined_rows = process_data(solid_report_data, platform_data, platform_columns)

        write_csv_file(header, combined_rows, csv_file_path)

        logger.info(f"Total records processed and written to CSV: {len(combined_rows)}")

        # Verificar el archivo CSV
        if os.path.exists(csv_file_path) and os.path.getsize(csv_file_path) > 0:
            logger.info(f"CSV file verified: {csv_file_path} ({os.path.getsize(csv_file_path)} bytes)")
        else:
            raise FileNotFoundError(f"CSV file not created or empty: {csv_file_path}")

        return csv_file_path

    except Exception as e:
        logger.error(f"Error in generate_csv_card_report: {e}", exc_info=True)
        raise

    finally:
        cursor_platform.close()
        conn_platform.close()
        logger.info("Database connections closed")