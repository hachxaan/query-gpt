import openai


class OpenAIAPIGetContextAdapter:
    def __init__(self, api_key: str):
        self.prompt_validation = \
"""
Instrucciones
Identifica el prompt del usuario final para determinar si la instrucción o confirmación pertenece a alguno de los siguientes contextos:

1: Generar un nuevo query.
2: Actualizar o ajustar un query ya creado.
3: Ajustar el template (html) o apariencia de una tabla datatables.
4: Ajustar el template (html) o apariencia de una gráfica highcharts.
5: Fuera de contexto.
Esta respuesta será utilizada para modificar el frontend con pasos adicionales.

Consideraciones:
Para tu respuesta solo regresa json.
Si no estás seguro de a cuál de los contextos pertenece, no decidas hasta que haya algo objetivo y devuelve el mensaje:
{{"code":"1", "request_type":"type_request", "respueta_chat": "[Respuesta breve de ChatGPT en lenguaje natural sin explicaciones extensas. La respuesta es para el usuario final y no debe ser técnica]"}}
Formato de Respuesta
Tu respuesta debe ser **unicamente en formato json** con las siguientes llaves:
{{"code":"0", "request_type":"type_request","respueta_chat": "[Respuesta de ChatGPT en lenguaje natural]"}}

Contexto 1: Generar un nuevo query
Prompt:
"Crear un nuevo query para obtener todos los registros de la tabla de empleados que tengan un salario superior a 5000."
Respuesta:
{{"code":"0", "request_type":"1","respueta_chat": "Entendido, se creará un nuevo query para filtrar los empleados con salario superior a 5000."}}


Contexto 2: Para actualizar o ajustar un query ya creado
Prompts de ejemplo:
"Modificar el query existente para incluir también a los empleados con salario igual a 5000."
"Elimina o quita el columna abc"
"Filtralos por abc"
Respuesta:
{{"code":"0", "request_type":"2","respueta_chat": "Entendido, se modificará el query existente para incluir a los empleados con salario igual a 5000."}}


Contexto 3: Actualizar la tabla
Prompt: "Agrega botones a la tabla para exportar los datos"
Ejemplo de Respuesta
{{"code":"0", "request_type":"3","respueta_chat": "Entendido, se agregarán botones para exportar los datos."}}


Contexto 4: Ajustar el template (html) o apariencia de un gráfica highcharts
Prompt:
"Modificar la gráfica existente para cambiar el color de fondo a azul."
Respuesta:
{{"code":"0", "request_type":"4","respueta_chat": "Entendido, se cambiará el color de fondo de la gráfica a azul."}}


Contexto 5: Fuera de contexto
Prompt:
"¿Cómo está el clima hoy?"
Respuesta:
{{"code":"0", "request_type":"5","respueta_chat": "Lo siento, esa pregunta está fuera de contexto y no puedo ayudarte con eso."}}

Notas Adicionales
Asegúrate de que tu respuesta sea concisa y clara, evitando términos técnicos cuando sea posible.
Verifica el contexto adecuado antes de enviar una respuesta definitiva.
Utiliza el contexto "5" cuando el prompt del usuario final sea irrelevante o no tenga relación con los contextos propuestos.

**Prompt de usuario:**
{user_prompt}



"""
        openai.api_key = api_key

    def get_context(
        self, user_prompt: str, max_tokens: int = 2000
    ):
        # Formatea el prompt con las tablas, campos y query
        prompt = self.prompt_validation.format(
            user_prompt=user_prompt
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



