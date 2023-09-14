import os
import openai


class OpenAIAPIQueryAdapter:
    def __init__(self, api_key: str):
        self.prompt_validation = """
            # Sentencia SELECT postgres:
            ({rules})
            
            ({tables_fields})

            
            Consideraciones:
            Si en las reglas no especifican los campos, utiliza los campos disponibles.
            Importante: No hagas join de tablas si no se ocupas ninguna campo de la misma.
            Para tu respuesta devuelve exclusivamente el sql query.

            Ocupa lo siguiente solo si es necesario (cuando se te pida por status_id o status)
            credits.status_id:[
            1:      created = ACH pendiente,
            12:     failed = failed,
            13:     approved = Credito,
            14:     wage_deduction : Deducción,
            15:     canceled : Cancelado,
            16:     wa_promotional_credit   WA Promotional Credit,
            17:     wa_refund       WA Refund
            ]

            credits.instant :[
            True: credito normal,
            False: ACH,
            NULL: deducciones,
            ]

            credit.status: [
            'ach' : ACH,
            'pending': pendientes,
            'paid': pagados,
            'pastDue': en past due,
            'chargedOff': charge off,
            'not_applied': dediccion no aplica status,
            'applied': dedicción aplicada
            ]
        """
        openai.api_key = api_key

    def get_query(
        self, tables_fields: str, rules: str, max_tokens: int = 2000
    ):
        # Formatea el prompt con las tablas, campos y query
        prompt = self.prompt_validation.format(
            tables_fields=tables_fields, rules=rules
        )
        print("-------------------------------------")
        print(prompt)
        print("-------------------------------------")
        # Crea la solicitud a la API de OpenAI
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=0.5,
            max_tokens=max_tokens,
        )

        # Retorna la respuesta
        return response.choices[0].text.strip()
