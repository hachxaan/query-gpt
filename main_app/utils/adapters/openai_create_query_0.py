import os
import openai


class OpenAIAPIQueryAdapter:
    def __init__(self, api_key: str):
        self.prompt_template = """
            **Consulta SELECT en Postgres:**
            {rules}

            Campos Disponibles. Aquí tienes las tablas y los campos que les pertenece a cada tabla.
            {tables_fields}
            
            Reglas y Consideraciones
            - Si el prompt no especifica qué campos de información usar, emplea los campos disponibles.
            - No generes consultas con "*". Enumera todos los campos disponibles de las tablas incluidas.
            - No realices join a otras tablas si no se utiliza ningún campo de estas tablas.
            - Solo devuelve la cadena del query
            Consideraciones Específicas
            {specific_considerations}
        """
        # - **IMPORTANTE: Devuelve unica y exclusivamente la cadena del SQL query.**
        # - **Devuelve únicamente la cadena del SQL query, sin ningún texto adicional, encabezado, o etiqueta.**
        # No añadas "### Respuesta:", "# Respuesta:" ni nada similar como: ### Solución: NADA DE ESTO. ***(((SOlO EL QUERY)))***
        # **Usa lo siguiente solo si es necesario:** 
        openai.api_key = api_key

    def format_tables_fields(self, tables_fields: list) -> str:
        formatted_str = ""
        for table, fields in tables_fields:
            formatted_str += f"- Tabla '{table}':\n  (" + ", ".join(fields) + ")\n"
        return formatted_str

    def get_query(self, tables_fields: str, rules: str, max_tokens: int = 2000):

        formatted_tables_fields = self.format_tables_fields(tables_fields=tables_fields)

        specific_considerations = """
        - usuarios = clientes, usuario = cliente
        - creditos = credito = Wage Access = wage acccess = WA = wa
        - fee = comision, fees = comisiones
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
        respuesta = self.extraer_query(response.choices[0].text.strip())
        print(respuesta)
        return respuesta


    def extraer_query(self, cadena: str) -> str:
        # Busca el índice del carácter ':' en la cadena.
        # Si no lo encuentra, regresa una cadena vacía.
        indice_dos_puntos = cadena.find(':')
        if indice_dos_puntos == -1:
            return ""
        
        # Extrae la subcadena desde el carácter siguiente al ':' hasta el final.
        query = cadena[indice_dos_puntos+1:].strip()
        
        return query
