import os
import openai
import json

class OpenAIAPIQueryAdapter:
    def __init__(self, api_key: str):
        self.prompt_template = """
            ### Task
            Generate a SQL query to answer [QUESTION]{rules}[/QUESTION]

            ### Instrucciones
            Campos Disponibles. Aquí tienes las tablas y los campos que les pertenece a cada tabla.
            {tables_fields}
            
            ### Reglas y Consideraciones
            - Si no puede responder la pregunta con el esquema de base de datos disponible, responda "No lo sé".
            - Si el prompt no especifica qué campos de información usar, emplea los campos disponibles.
            - No generes consultas con "*". Enumera todos los campos disponibles de las tablas incluidas.
            - No realices join a otras tablas si no se utiliza ningún campo de estas tablas.
            
            ### Consideraciones Específicas
            - Estas reglas son obligatorias e importantes.
            {specific_considerations}

            ### Formato de respuesta:
            {formato_respueta}
        """

        openai.api_key = api_key

    def format_tables_fields(self, tables_fields: list) -> str:
        formatted_str = ""
        for table, fields in tables_fields:
            formatted_str += f"- Tabla '{table}':\n  (" + ", ".join(fields) + ")\n"
        return formatted_str

    def get_query(self, tables_fields: str, rules: str, max_tokens: int = 3000):

        formatted_tables_fields = self.format_tables_fields(tables_fields=tables_fields)

        specific_considerations = """ 
        - Respeta los campos con guión bajo, por ejemplo _last_name debe ser _last_name.
        - usuarios = clientes, usuario = cliente, empleado = user
        - creditos = credito = Wage Access = wage acccess = WA = wa = EWA
        - fee = comision, fees = comisiones
        - Para saber si un usuario tiene banking, se debe revisar si el campo users.customer_uuid no es nulo.
        - Para las relaciones de las tablas: 
            users.company_id = companies.id
            credits.user_id = user.id
            credits.status_id = credit_status.id
        - Para credits.status_id. Es el tipo de registro en la tabla credits:
            1: created = ACH pendiente
            12: failed = failed
            13: approved = Crédito
            14: wage_deduction = Deducción
            15: canceled = Cancelado
            16: wa_promotional_credit = WA Promotional Credit
            17: wa_refund = WA Refund
        - Para credits.instant:
            True: crédito normal
            False: ACH
            NULL: deducciones
        - Para credit.status, es el estado del pago del credito, es el estatus del credito, o status o situación o "créditos que están":
            'ach': ACH
            'pending': pendientes
            'paid': pagados
            'pastDue': en past due
            'chargedOff': charge off
            'not_applied': deducción no aplica status
            'applied': deducción aplicada
        - Para users.payroll_type:
            1: Daily
            2: Hourly
        - Para credits.type
            'Recurrent Solid Credit': Auto wage access vía Solid
            'Recurrent Tabapay Credit': Auto wage access vía Tabapay
            'Regular ACH Credit': ACH vía Tabapay
            'Regular Solid Credit': Instantaneo vía Solid
            'Regular Tabapay Credit': Instantaneo vía Tabapay
            'wage_access': Sin catalogar, pudieron ser Auto wage access o instantaneo, ambos vía Tabapay
        """
        
        formato_respueta = 'Tu respueste debe ser en formato json con las llaves: {"respueta_chat": "[Respuesta de chatgpt de sus comentarios o preguntas en lengueje natural, debe ser corta sin tanta explicación]", "query": "SELECT ...", "field_info": "[Lista de campos de la respuesta, serán utilizados para la implementación en la librería hightchats]"}'
        # Formatea el prompt con las tablas, campos y query
        prompt = self.prompt_template.format(
            tables_fields=formatted_tables_fields, 
            rules=rules, 
            specific_considerations=specific_considerations, 
            formato_respueta=formato_respueta
        )
        print("-------------------------------------")
        print(prompt)
        print("-------------------------------------")
        
        # # Crea la solicitud a la API de OpenAI
        # response = openai.Completion.create(
        #     model="gpt-3.5-turbo",
        #     prompt=prompt,
        #     temperature=0.0,
        #     max_tokens=max_tokens,
        # )



        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": 'You are a SQL Postgres Programer'},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=max_tokens,
        )



        # Retorna la respuesta
        respuesta = self.extraer_query(response.choices[0].message.content.strip())
        print(respuesta)
        return respuesta


    def extraer_query(self, cadena: str) -> str:
        # Busca el índice del carácter ':' en la cadena.
        # Si no lo encuentra, regresa una cadena vacía.
        # dict_response = json.loads(json_string)
        
        cadena = cadena.replace('```json\n', '').replace('\n```', '')
        return json.loads(cadena)


