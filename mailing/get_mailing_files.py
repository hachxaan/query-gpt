import base64
import os
import csv
import psycopg2
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configuración de la base de datos
DB_USER = os.getenv('POSTGRES_USER')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')
DB_NAME = os.getenv('POSTGRES_DB')
DB_HOST = os.getenv('POSTGRES_DNS')
DB_PORT = os.getenv('POSTGRES_PORT')
DB_KEY = os.getenv('DB_KEY')

def decode_base64(data):
    """
    Decodifica una cadena en base64, ajustando el relleno si es necesario.
    """
    if isinstance(data, (bytes, memoryview)):
        return data  # Si 'data' ya es bytes o memoryview, no necesita decodificación base64.
    
    # Asegura que 'data' sea una cadena para ajustar el relleno.
    if not isinstance(data, str):
        data = str(data, encoding='utf-8')
    
    padding = 4 - (len(data) % 4)
    data += "=" * padding
    return base64.b64decode(data)

# Clase Fernet para desencriptación actualizada
class FernetSingleton:
    class __FernetSingleton:
        def __init__(self):
            key_str = os.getenv('DB_KEY')
            key_bytes = key_str.encode('utf-8')
            self.fernet = Fernet(key_bytes)
    instance = None

    def __init__(self):
        if not FernetSingleton.instance:
            FernetSingleton.instance = FernetSingleton.__FernetSingleton().fernet

    def __getattr__(self, name):
        return getattr(self.instance, name)

# Crear conexión a la base de datos
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)

cursor = conn.cursor()

# Consulta SQL
query = """
SELECT 
"Email Address", 
"First Name", 
"Last Name", 
"User ID", 
"White Label", 
"Label Customer Service", 
"Tags", 
"Card Number", 
"Company Name",
"file_name"
FROM vw_mailings
ORDER BY "file_name"
"""

cursor.execute(query)
rows = cursor.fetchall()
columns = [desc[0] for desc in cursor.description]

# Instancia de Fernet para desencriptar
fernet = FernetSingleton()

# Inicializar variables
current_file_name = ""
csv_writer = None
file = None
record_count = 0

total = len(rows)
current_row = 0
for row in rows:
    current_row += 1
    print(f"Processing row {current_row} of {total}")
    email_encrypted = row[0]
    first_name_encrypted = row[1]
    
    # Uso de la función ajustada para decodificar
    email_bit = decode_base64(email_encrypted)
    email = fernet.decrypt(email_bit).decode("utf-8")

    first_name_bit = decode_base64(first_name_encrypted)
    first_name = fernet.decrypt(first_name_bit).decode("utf-8")
    
    file_name = row[-1]
    
    if current_file_name != file_name:
        if file:
            file.close()
            file_name = f"{file_name_prefix}_{record_count}.csv"
            os.rename(temp_file_name, file_name)
            print(f"Saved {file_name}")

        
        current_file_name = file_name
        record_count = 0
        file_name_prefix = file_name.rsplit('_', 1)[0]
        temp_file_name = f"{file_name_prefix}_temp.csv"
        file = open(temp_file_name, mode='w', newline='', encoding='utf-8')
        csv_writer = csv.writer(file)
        csv_writer.writerow(columns[:-1])  # Exclude "file_name"
    
    row = [email, first_name] + list(row[2:-1])
    csv_writer.writerow(row)
    record_count += 1

if file:
    file.close()
    os.rename(temp_file_name, f"{file_name_prefix}_{record_count}.csv")

cursor.close()
conn.close()