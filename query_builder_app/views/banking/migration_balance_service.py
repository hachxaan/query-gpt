import os
import sys
import psycopg2
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import csv
from datetime import datetime
import logging
import tempfile

logger = logging.getLogger(__name__)

load_dotenv()

query_migration = """
    SELECT
    white_label_tag,
    c."name",
    u.id AS "user_id",
    u.email_old AS "email",
    u."_flags" ->> 'migration_status',
    dsolid.available_balance,
    dsolid.id AS "accountId",
    dsolid.created_person_id AS "personId",
    dsolid.status,
    dsolid."type",
    u.first_name,
    u."_last_name"
    FROM users u
    JOIN companies c ON c.id = u.company_id
    LEFT JOIN user_accounts_solid_temp dsolid ON dsolid.user_id = u.id
    WHERE u."_flags" ->> 'migration_status' in ('started', 'declined')
    ORDER BY white_label_tag, u.first_name
"""

def generate_migration_balance_report():
    temp_dir = '/home/administrador/temp-files'
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_file_path = os.path.join(temp_dir, f'migration_balance_report_{timestamp}.csv')
    
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("POSTGRES_DNS"),
            port=os.getenv("POSTGRES_PORT")
        )
        
        cursor = conn.cursor()
        cursor.execute(query_migration)
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(columns)
            
            for row in results:
                processed_row = []
                for i, value in enumerate(row):
                    column_name = columns[i]
                    if column_name.startswith('_') and column_name != '_flags':
                        processed_row.append(decrypt_value(value, i, column_name))
                    else:
                        processed_row.append(value)
                writer.writerow(processed_row)
                
        return csv_file_path
        
    except Exception as e:
        logger.error(f"Error generating migration balance report: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()
