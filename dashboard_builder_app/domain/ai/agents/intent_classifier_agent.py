import json
from openai import OpenAI


from .llm_base import LlmBase

class IntentClassifier(LlmBase):
    def __init__(self):
        self.api = OpenAI()
        self.model_name = "gpt-3.5-turbo-instruct"

    def classify_intent(self, user_input):
        prompt = f"""
        Por favor identifica la intención del usuario según el mensaje proporcionado y responde con un JSON en forma de cadena. Las opciones son:
        1: Crear un query SQL para obtener nuevos resultados.
        2: Actualizar un query SQL existente; Aplica: cuando se hable sobre filtros, agrupar, actualizar campos, etc.
        3: Modificar el código fuente de la tabla datatables.
        4: Modificar el código fuente de la gráfica highchart.
        5: Consejo u opinión a partir de la evalueción de la Eficiencia del Dashboard
        5: Otro contexto.

        - **NOTA IMPORTANTE:** A menos que el usuario solicite explicitamente un cambio a la gráfica o la visualización de la información, selecciona la opción 1 o 2 según corresponda.
        - **Nota:** Si la intención no encaja en ninguna de las opciones anteriores, selecciona la opción 5.

        Mensaje del usuario: **{user_input}**

        Ejemplos:
        - Si el usuario pide "Obtener a los usuarios que no han iniciado sesión en los últimos 30 días...", la respuesta es:
            "code": "1",
            "message": "Estoy trabajando en el query para obtener esa información."
        - Si el usuario dice "Agrega hover al pasar el mouse a los rows de la tabla...", la respuesta es:
            "code": "3",
            "message": "Preparando la actualización para mejorar la interactividad de la tabla."


        Contexto: El frontend es un constructor de dashboards BI, y el usuario solicitará cambios. A partir de la intención detectada, se solicitarán los cambios al modelo especializado según la tarea.
        """

        prompt += '\n- IMPORTANTE: Formato de respuesta esperado JSON con las siguientes llaves: {"code": "[número de opción]", "message": "[Mensaje corto para el usuario final]"}"'
        try:
            response = self.api.completions.create(
                model=self.model_name,
                prompt=prompt,
                max_tokens=100,  
                temperature=0.2,  # Ligeramente más creativo, pero todavía muy controlado
                stop=None  
            )

            # Procesar y validar la respuesta
            try:
                result = json.loads(response.choices[0].text.strip())
                if 'code' not in result or 'message' not in result:
                    raise ValueError("La respuesta del modelo no cumple con el formato esperado.")
            except json.JSONDecodeError:
                raise ValueError("La respuesta del modelo no es un JSON válido.")
            except KeyError:
                raise ValueError("La respuesta del modelo no contiene las llaves requeridas.")
                
            return result

        except Exception as e:
            print(f"Error al obtener la intención: {e}")


# if __name__ == "__main__":
#     user_input = "Actualiza la grafica"
#     classifier = IntentClassifier()
#     result = classifier.classify_intent(user_input)
#     print(result)