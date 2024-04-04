import os
import openai


class OpenAIAPITableAdapter:
    def __init__(self, api_key: str):
        self.prompt_template = """
            **Consulta SELECT en Postgres:**
            {rules}

            ### Campos Disponibles
            {tables_fields}
            
            ### Reglas y Consideraciones:
            - Si el prompt no especifica qué campos de información usar, emplea los campos disponibles.
            - No generes consultas con "*". Enumera todos los campos disponibles de las tablas incluidas.
            - No realices join a otras tablas si no se utiliza ningún campo de estas tablas.
            - Devuelve exclusivamente el SQL query en tu respuesta. No añadas "# Respuesta:" ni nada similar como: ### Solución: NADA DE ESTO. ***(((SOlO EL QUERY)))***

            ### Consideraciones Específicas:
            **Usa lo siguiente solo si es necesario:**
            {specific_considerations}
        """
        openai.api_key = api_key

    def format_tables_fields(self, tables_fields: list) -> str:
        formatted_str = ""
        for table, fields in tables_fields:
            formatted_str += f"- Tabla '{table}':\n  - " + ", ".join(fields) + "\n"
        return formatted_str


    def get_query(self, tables_fields: str, rules: str, max_tokens: int = 2000):

        formatted_tables_fields = self.format_tables_fields(tables_fields=tables_fields)

        specific_considerations = """
        - Para status_id o status o estatus o situación o "créditos que están":
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
        - Para credit.status:
            'ach': ACH
            'pending': pendientes
            'paid': pagados
            'pastDue': en past due
            'chargedOff': charge off
            'not_applied': deducción no aplica status
            'applied': deducción aplicada
        """
        
        # Formatea el prompt con las tablas, campos y query
        prompt = self.prompt_template.format(
            tables_fields=formatted_tables_fields, rules=rules, specific_considerations=specific_considerations
        )
        print("-------------------------------------")
        print(prompt)
        print("-------------------------------------")
        
        # Crea la solicitud a la API de OpenAI
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=0.0,
            max_tokens=max_tokens,
        )

        # Retorna la respuesta
        respuesta = response.choices[0].text.strip()
        print(respuesta)
        return respuesta
