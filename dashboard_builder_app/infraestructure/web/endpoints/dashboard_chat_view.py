# dashboard_builder_app/infraestructure/web/endpoints/dashboard_create_view.py

import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.middleware.csrf import CsrfViewMiddleware
from django.views.decorators.csrf import csrf_exempt
from dashboard_builder_app.application.services.config_dashboard_application_service import ConfigDashboardApplicationService
from dashboard_builder_app.infraestructure.persistence.adapters.main_chat_repository_adapter import MainChatRespositoryAdapter
from dashboard_builder_app.infraestructure.persistence.adapters.dashboard_repository_adapter import DashboaradRespositoryAdapter
from dashboard_builder_app.infraestructure.persistence.services.chat_proxy_orm_service import ChatProxyORMService
from dashboard_builder_app.infraestructure.persistence.services.dashboard_orm_service import DashboardORMService
from dashboard_builder_app.shared.ddd.domain.model.Id import Id

@require_POST
@csrf_exempt
def dashboard_chat_view(request, uuid):
    try:
        chat_proxy_orm_service = ChatProxyORMService()
        chats_history_repository_adapter = MainChatRespositoryAdapter(chat_proxy_orm_service=chat_proxy_orm_service)
        dashboard_repository_adaptaer = DashboaradRespositoryAdapter(dashboard_orm_service=DashboardORMService())
        
        config_dashboard_service = ConfigDashboardApplicationService(
            main_chat_repository=chats_history_repository_adapter,
            dashboard_repository=dashboard_repository_adaptaer,
            dashboard_uuid=Id.ofString(uuid)
        )

        data = config_dashboard_service.process_message(
            request=json.loads(request.body)
        )
            
        return JsonResponse(data)

    except CsrfViewMiddleware:
        return JsonResponse({'success': False, 'error': 'CSRF verification failed. Request aborted.'})
    except Exception as e:
        print("\033[91m" + str(e) + "\033[0m")
        return JsonResponse({'success': False, 'error': str(e)})
