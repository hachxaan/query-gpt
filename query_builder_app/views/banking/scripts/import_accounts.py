import os
import json
import psycopg2
from psycopg2.extras import Json
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de base de datos
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_HOST = os.getenv("POSTGRES_DNS")
DB_PORT = os.getenv("POSTGRES_PORT")


# Configuración de base de datos operacional
OP_POSTGRES_USER = os.getenv('OPERATION_USER')
OP_POSTGRES_PASSWORD = os.getenv('OPERATION_PASSWORD')
OP_POSTGRES_DB = os.getenv('OPERATION_DB')
OP_POSTGRES_PORT = os.getenv('OPERATION_PORT')
OP_POSTGRES_DNS = os.getenv('OPERATION_DNS')

# Configuración de la API
SOLID_API_KEY = os.getenv("SOLID_API_KEY")
SOLID_BASE_URL = os.getenv("SOLID_BASE_URL")
PROGRAM_ID = os.getenv("PROGRAM_ID")
SD_PERSON_ID = os.getenv("SD_PERSON_ID")

# Archivo JSON local
JSON_FILE_PATH = "accounts_data.json"

# Tabla donde se guardarán los datos
TABLE_NAME = "user_accounts_solid_temp"

class AccountsApiService:
    ACCOUNTS_PROGRAM = "/v1/program/{}/account"

    def __init__(self, base_url, api_key, program_id, sd_person_id):
        self.base_url = base_url
        self.api_key = api_key
        self.program_id = program_id
        self.sd_person_id = sd_person_id
        self.records = []
        self.query_params = {"limit": 100, "offset": 0}

    def _get_headers(self):
        return {
            "sd-api-key": self.api_key,
            "sd-person-id": self.sd_person_id
        }

    def fetch_all(self):
        if os.path.exists(JSON_FILE_PATH):
            print("Cargando datos desde archivo JSON local...")
            with open(JSON_FILE_PATH, 'r') as file:
                self.records = json.load(file)
            return self.records

        print("Obteniendo datos desde la API...")
        while True:
            self.query_params["offset"] = len(self.records)
            print(f"Buscando cuentas: offset={self.query_params['offset']}, total={len(self.records)}")
            
            response = requests.get(
                self.base_url + self.ACCOUNTS_PROGRAM.format(self.program_id),
                headers=self._get_headers(),
                params=self.query_params
            )
            
            if response.status_code != 200:
                raise Exception(f"API Request failed with status {response.status_code}: {response.text}")

            data = response.json()
            if not data or "data" not in data:
                break

            self.records.extend(data["data"])

            if len(data["data"]) < self.query_params["limit"]:
                break

        print("Guardando datos en archivo JSON local...")
        with open(JSON_FILE_PATH, 'w') as file:
            json.dump(self.records, file, indent=2)

        return self.records



def get_user_id(account_id):
    connection = psycopg2.connect(
        dbname=OP_POSTGRES_DB, 
        user=OP_POSTGRES_USER, 
        password=OP_POSTGRES_PASSWORD, 
        host=OP_POSTGRES_DNS, 
        port=OP_POSTGRES_PORT
    )
    cursor = connection.cursor()
    
    cursor.execute("""
        SELECT "userId" 
        FROM customer 
        WHERE "accountId" = %s
    """, (account_id,))
    
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    
    return result[0] if result else None

def clean_accounts_table():
    connection = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )
    cursor = connection.cursor()


    cursor.execute(f"TRUNCATE TABLE {TABLE_NAME}")
    connection.commit()
    
    cursor.close()
    connection.close()
    print("Tabla limpiada exitosamente")

def insert_accounts(records):
    connection = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )
    
    print("Limpiando tabla user_accounts_solid_temp...")
    print(f"Tabla: {TABLE_NAME}")
    print(f"Usuario: {DB_USER}")
    print(f"Contraseña: {DB_PASSWORD}")
    print(f"Host: {DB_HOST}")
    print(f"Puerto: {DB_PORT}")
    print(f"Base de datos: {DB_NAME}")

    
    cursor = connection.cursor()

    insert_query = f"""
    INSERT INTO {TABLE_NAME} (
        id, user_id, accepted_terms, account_interest_frequency,
        available_balance, business_id, config, created_at, created_person_id,
        currency, family_id, fees, interest, is_verified, label, metadata,
        modified_at, pending_credit, pending_debit, program_id,
        sponsor_bank_name, status, type
    )
    VALUES (
        %(id)s, %(user_id)s, %(acceptedTerms)s, %(accountInterestFrequency)s,
        %(availableBalance)s, %(businessId)s, %(config)s, %(createdAt)s,
        %(createdPersonId)s, %(currency)s, %(familyId)s, %(fees)s, %(interest)s,
        %(isVerified)s, %(label)s, %(metadata)s, %(modifiedAt)s, %(pendingCredit)s,
        %(pendingDebit)s, %(programId)s, %(sponsorBankName)s,
        %(status)s, %(type)s
    )
    ON CONFLICT (id) DO UPDATE SET
        user_id = EXCLUDED.user_id,
        accepted_terms = EXCLUDED.accepted_terms,
        account_interest_frequency = EXCLUDED.account_interest_frequency,
        available_balance = EXCLUDED.available_balance,
        business_id = EXCLUDED.business_id,
        config = EXCLUDED.config,
        created_at = EXCLUDED.created_at,
        created_person_id = EXCLUDED.created_person_id,
        currency = EXCLUDED.currency,
        family_id = EXCLUDED.family_id,
        fees = EXCLUDED.fees,
        interest = EXCLUDED.interest,
        is_verified = EXCLUDED.is_verified,
        label = EXCLUDED.label,
        metadata = EXCLUDED.metadata,
        modified_at = EXCLUDED.modified_at,
        pending_credit = EXCLUDED.pending_credit,
        pending_debit = EXCLUDED.pending_debit,
        program_id = EXCLUDED.program_id,
        sponsor_bank_name = EXCLUDED.sponsor_bank_name,
        status = EXCLUDED.status,
        type = EXCLUDED.type;
    """

    for index, record in enumerate(records):
        try:
            if index == 30:
                break
            user_id = get_user_id(record["id"])
            
            cursor.execute(insert_query, {
                "id": record["id"],
                "user_id": user_id,
                "acceptedTerms": record["acceptedTerms"],
                "accountInterestFrequency": record["accountInterestFrequency"],
                "availableBalance": record["availableBalance"],
                "businessId": record.get("businessId", ""),
                "config": Json(record["config"]),
                "createdAt": record["createdAt"],
                "createdPersonId": record["createdPersonId"],
                "currency": record["currency"],
                "familyId": record.get("familyId", ""),
                "fees": record["fees"],
                "interest": record["interest"],
                "isVerified": record["isVerified"],
                "label": record["label"],
                "metadata": Json(record.get("metadata", {})),
                "modifiedAt": record["modifiedAt"],
                "pendingCredit": record["pendingCredit"],
                "pendingDebit": record["pendingDebit"],
                "programId": record["programId"],
                "sponsorBankName": record["sponsorBankName"],
                "status": record["status"],
                "type": record["type"]
            })
            print(f"Cuenta {record['id']} insertada con user_id: {user_id}")
        except Exception as e:
            print(f"Error al insertar cuenta con id={record.get('id')}: {e}")
            raise e

    connection.commit()
    cursor.close()
    connection.close()

def import_accounts_from_solid():
    print("Iniciando importación de cuentas...")
    
    clean_accounts_table()

    api_service = AccountsApiService(
        base_url=SOLID_BASE_URL,
        api_key=SOLID_API_KEY,
        program_id=PROGRAM_ID,
        sd_person_id=SD_PERSON_ID
    )

    records = api_service.fetch_all()

    print(f"Se obtuvieron {len(records)} cuentas. Iniciando inserción en la base de datos...")

    insert_accounts(records)

    print("Importación de cuentas completada.")

