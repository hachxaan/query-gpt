import os
import csv
import psycopg2
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import base64
from datetime import datetime

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configuración de la base de datos
DB_USER = os.getenv('POSTGRES_USER')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')
DB_NAME = os.getenv('POSTGRES_DB')
DB_HOST = os.getenv('POSTGRES_DNS')
DB_PORT = os.getenv('POSTGRES_PORT')
DB_KEY = os.getenv('DB_KEY')

# Clase Fernet para desencriptación
class FernetSingleton:
    class __FernetSingleton:
        def __init__(self) -> Fernet:
            key_bytes = DB_KEY.encode('utf-8')
            self.fernet = Fernet(key_bytes)
    instance = None

    def __init__(self) -> Fernet:
        if not FernetSingleton.instance:
            FernetSingleton.instance = FernetSingleton.__FernetSingleton().fernet

    def __getattr__(self, name):
        return getattr(self.instance, name)

# Inicializa el singleton de Fernet
fernet = FernetSingleton()

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
"Last Name", 
"First Name", 
"User ID", 
"White Label", 
"Label Customer Service", 
"Tags", 
"Card Number", 
"Company Name",
"file_name"
FROM vw_mailings_v2
ORDER BY "file_name"
"""

cursor.execute(query)
rows = cursor.fetchall()
columns = [desc[0] for desc in cursor.description]

# Inicializar variables
current_file_name = ""
csv_writer = None
record_count = 0
files_generated = []

total = len(rows)
current_row = 0

def is_base64(s):
    try:
        if isinstance(s, str):
            s_bytes = s.encode('utf-8')
        elif isinstance(s, memoryview):
            s_bytes = s.tobytes()
        else:
            s_bytes = s
        base64.urlsafe_b64decode(s_bytes)
        return True
    except Exception:
        return False

# Nombre de la carpeta con la fecha de hoy
today_date = datetime.now().strftime('%Y%m%d')
directory_name = f"files_{today_date}"

# Crear la carpeta si no existe
if not os.path.exists(directory_name):
    os.makedirs(directory_name)
else:
    # Borrar los archivos CSV existentes si la carpeta ya existe
    for file in os.listdir(directory_name):
        if file.endswith(".csv"):
            os.remove(os.path.join(directory_name, file))

file = None
for row in rows:
    current_row += 1
    print(f"Processing row {current_row} of {total}")
    email_encrypted = row[0]
    last_name_encrypted = row[1]
    
    # Convertir memoryview a bytes si es necesario
    if isinstance(email_encrypted, memoryview):
        email_encrypted = email_encrypted.tobytes()
    if isinstance(last_name_encrypted, memoryview):
        last_name_encrypted = last_name_encrypted.tobytes()
    
    try:
        # Verificar si los datos son base64 válidos antes de desencriptar
        if is_base64(email_encrypted):
            email = fernet.decrypt(email_encrypted).decode("utf-8")
        else:
            print(f"Invalid base64 for email: {email_encrypted}")
            email = None

        if is_base64(last_name_encrypted):
            last_name = fernet.decrypt(last_name_encrypted).decode("utf-8")
        else:
            print(f"Invalid base64 for first name: {last_name_encrypted}")
            last_name = None

    except Exception as e:
        print(f"Error decrypting row {current_row}: {e}")
        email = None
        last_name = None

    file_name = row[-1]
    
    if current_file_name != file_name:
        if file:
            file.close()
            final_file_name = os.path.join(directory_name, f"{file_name_prefix}_{record_count}.csv")
            os.rename(temp_file_name, final_file_name)
            print(f"Saved {final_file_name}")
            files_generated.append(final_file_name)

        current_file_name = file_name
        record_count = 0
        if not file_name:
            file_name_prefix = "202407_unknown"
        else:
            file_name_prefix = file_name.rsplit('_', 1)[0]
        temp_file_name = os.path.join(directory_name, f"{file_name_prefix}_temp.csv")
        file = open(temp_file_name, mode='w', newline='', encoding='utf-8')
        csv_writer = csv.writer(file)
        csv_writer.writerow(columns[:-1])  # Exclude "file_name"
    
    row = [email, last_name] + list(row[2:-1])
    csv_writer.writerow(row)
    record_count += 1

if file:
    file.close()
    final_file_name = os.path.join(directory_name, f"{file_name_prefix}_{record_count}.csv")
    os.rename(temp_file_name, final_file_name)
    print(f"Saved {final_file_name}")
    files_generated.append(final_file_name)

# Crear un CSV con la lista de los archivos generados
with open(os.path.join(directory_name, 'files_generated.csv'), mode='w', newline='', encoding='utf-8') as file_list:
    csv_writer = csv.writer(file_list)
    csv_writer.writerow(['file_name'])
    for file_name in files_generated:
        csv_writer.writerow([file_name])

cursor.close()
conn.close()