



from datetime import datetime
import json
from dashboard_builder_app.domain.ai.agents.intent_classifier_agent import IntentClassifier
from dashboard_builder_app.domain.ai.agents.query_builder_agent import QueryBuilderAgent
from dashboard_builder_app.domain.entities.classifier_entity import ClassifierEntity
from dashboard_builder_app.domain.repositories.dashboard_repository import IDashboard
from dashboard_builder_app.domain.repositories.main_chat_repository import IMainChat
from dashboard_builder_app.shared.ddd.domain.model.Id import Id
from backoffice.utils import get_session_user

class ConfigDashboardApplicationService:
    def __init__(
            self, 
            main_chat_repository: IMainChat,
            dashboard_repository: IDashboard,
            dashboard_uuid: Id
        ):
        self.main_chat_repository = main_chat_repository
        self.dashboard_repository = dashboard_repository
        self.user = get_session_user()
        self.dashboard_uuid = dashboard_uuid

    def get_config(self) -> dict:
        proxy_chat = self.main_chat_repository.get_chat_history(dashboard_uuid=self.dashboard_uuid)
        dashboard_config = self.dashboard_repository.get_dashboard(uuid=self.dashboard_uuid)

        return {
            "dashboard_uuid": self.dashboard_uuid.value,
            "chat_history": proxy_chat,
            "dashboard_config": None # dashboard_config
        }   

    def save_user_message(self, user_message: str) -> None: 
        self.main_chat_repository.add_formatted_message_to_chat(
            dashboard_uuid=self.dashboard_uuid,
            message_json={
            "sender": self.user.username,
            "text": user_message,
            "request_type": None,
        })

    def save_ai_message(self, ai_message: str, request_type: int) -> None: 
        self.main_chat_repository.add_formatted_message_to_chat(
            dashboard_uuid=self.dashboard_uuid,
            message_json={
            "sender": 'AI',
            "text": ai_message,
            "request_type": request_type,
        })


    def process_message(self, request: dict) -> dict:
        user = get_session_user()
        user_prompt = request.get('prompt', '') 
        try:
            self.save_user_message(user_prompt)
            classifier = IntentClassifier()
            intent = classifier.classify_intent(user_prompt)
            # self.save_ai_message(
            #     ai_message=intent['message'],
            #     request_type=intent['code'])
            


            # # if get_request_type.get('request_type') = [1,2]: # Query
            # # return JsonResponse(json.dumps(get_request_type))
            # # respuesta = validate_and_extract(get_request_type)

            # # session['query'] = None
            respuesta = {}
            if int(intent['code']) not in [1, 2] :
                intent['code'] = 2
            if int(intent['code']) in [1, 2] or 1 == 1:
        
                                
                db = QueryBuilderAgent(dashboard_uuid=self.dashboard_uuid, user_id=user.id)
                data = db.get_data(user_prompt)
                

                data_list_dict = [
                    {key: (lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if isinstance(x, datetime) else str(x))(value)
                    for key, value in zip(data['fields_list'], record)}
                    for record in data['data_tupla']
                ]


                print(json.dumps(data_list_dict, indent=4))


                message = self.main_chat_repository.add_formatted_message_to_chat(
                    dashboard_uuid=self.dashboard_uuid,
                    message_json={
                    "sender": 'AI',
                    "text": intent['message'],
                    "request_type": intent['code'],
                     "query": data['query'],
                })
                message_str = json.dumps(message)
                return {
                    "message": message_str,
                    "data": data_list_dict,
                    "fields": data['fields_list'],
                    "query": data['query'],
                    "code": intent['code'],

                }

            # process_instance = process.objects.get(id=session_id)  # Obtener una instancia del modelo
            # message_json = {
            #     "sender": "GPT",
            #     "text": intent['message'],
            #     "request_type": intent['code'],
            #     "query": data['query'],
            # }
            # process_instance.add_formatted_message_to_chat_history(message_json)

            return intent

        except Exception as e:
            print("\033[91m" + str(e) + "\033[0m")
            # return JsonResponse({"error": str(e)}, status=500)