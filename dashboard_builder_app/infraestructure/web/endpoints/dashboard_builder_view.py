# dashboard_builder_app/infraestructure/web/endpoints/dashboard_builder_view.py

import json
from django.http import Http404
from dashboard_builder_app.infraestructure.exception.dashboard_not_found_exception import DashboardNotFoundException
from dashboard_builder_app.infraestructure.persistence.adapters.dashboard_repository_adapter import DashboaradRespositoryAdapter
from dashboard_builder_app.infraestructure.persistence.services.dashboard_orm_service import DashboardORMService
from dashboard_builder_app.shared.ddd.domain.model.Id import Id
from django.shortcuts import render
from dashboard_builder_app.application.services.config_dashboard_application_service import ConfigDashboardApplicationService
from dashboard_builder_app.infraestructure.persistence.adapters.main_chat_repository_adapter import MainChatRespositoryAdapter
from dashboard_builder_app.infraestructure.persistence.services.chat_proxy_orm_service import ChatProxyORMService


def dashboard_builder_view(request, uuid):

    try:
        chat_proxy_orm_service = ChatProxyORMService()
        chats_history_repository_adapter = MainChatRespositoryAdapter(chat_proxy_orm_service=chat_proxy_orm_service)
        dashboard_repository_adaptaer = DashboaradRespositoryAdapter(dashboard_orm_service=DashboardORMService())
        
        config_dashboard_service = ConfigDashboardApplicationService(
            main_chat_repository=chats_history_repository_adapter,
            dashboard_repository=dashboard_repository_adaptaer,
            dashboard_uuid=Id.ofString(uuid)
        )

        chat_proxy_history = config_dashboard_service.get_config()

        # data = {
        #     'dashboard_uuid': uuid,
        #     'chat_proxy_history': chat_proxy_history
        # }

        print(json.dumps(chat_proxy_history, indent=4))

        return render(request, 'dashboard_builder/dashboard_builder.html', chat_proxy_history)
    
    except DashboardNotFoundException as e:
        raise Http404(e.message)
    except Exception as e:
        return render(request, 'error.html', {'error': str(e)})