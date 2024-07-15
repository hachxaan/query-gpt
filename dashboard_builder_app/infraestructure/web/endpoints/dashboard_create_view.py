# dashboard_builder_app/infraestructure/web/endpoints/dashboard_create_view.py

from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.middleware.csrf import CsrfViewMiddleware
from django.views.decorators.csrf import csrf_exempt
from dashboard_builder_app.application.services.create_dashboard_application_service import CreateDashboardApplicationService
from dashboard_builder_app.infraestructure.persistence.adapters.dashboard_repository_adapter import DashboaradRespositoryAdapter
from dashboard_builder_app.infraestructure.persistence.services.dashboard_orm_service import DashboardORMService

@require_POST
@csrf_exempt
def dashboard_create_view(request):
    try:
        create_dashboard_service = CreateDashboardApplicationService(
            DashboaradRespositoryAdapter(dashboard_orm_service=DashboardORMService())
        )
        dashboard_dict = create_dashboard_service.create_dashboard()
        dashboard_url = reverse('dashboard_builder_app:dashboard_builder', args=[dashboard_dict.get('uuid')])
        return JsonResponse({'success': True, 'redirect_url': dashboard_url})
    except CsrfViewMiddleware:
        return JsonResponse({'success': False, 'error': 'CSRF verification failed. Request aborted.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
