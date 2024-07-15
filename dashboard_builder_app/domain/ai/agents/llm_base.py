


import os
import psycopg2


class LlmBase:
    def connect_to(self, dbname: str):
        return psycopg2.connect(
            dbname=dbname,
            user=os.getenv("USER_DB"),
            password=os.getenv("PASSWORD_DB"),
            host=os.getenv("HOST_DB"),
            port=os.getenv("PORT_DB")
        )

    
    def connect_to_platform(self):
        return psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("POSTGRES_DNS"),
            port=os.getenv("POSTGRES_PORT")
        )