import os
import openai


class OpenAIAPIAdapter:
    def __init__(self, api_key: str):
        self.prompt_validation = """
            Tengo un query SQL y algunas reglas de validación:
            1. El query debe ser válido.
            2. Debe ser exclusivamente un SELECT.
            3. Solo debe consultar las tablas {tables} y los campos {fields}.
            4. Impotante! -> Solo debe consultar los fields {fields} <-.
            Aquí está el query: "{query}".

            Si el query cumple con todas las reglas, devuelve 'status: OK'. 
            Si no cumple con alguna de las reglas, devuelve 'status: ERROR' y especifica qué regla(s) no cumple.
        """
        openai.api_key = api_key

    def validate_query(
        self, tables: str, fields: str, query: str, max_tokens: int = 2000
    ):
        # Formatea el prompt con las tablas, campos y query
        prompt = self.prompt_validation.format(
            tables=tables, fields=fields, query=query
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
