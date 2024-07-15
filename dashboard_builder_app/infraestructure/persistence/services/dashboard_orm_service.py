# dashboard_builder_app/infraestructure/persistence/services/chat_proxy_orm_service.py

from dashboard_builder_app.infraestructure.exception.dashboard_not_found_exception import DashboardNotFoundException
from dashboard_builder_app.infraestructure.persistence.models.dashboard import DashboardModel
from dashboard_builder_app.shared.ddd.domain.model.Id import Id
from django.core.exceptions import ObjectDoesNotExist
from dashboard_builder_app.domain.entities.dashboard_entity import DashboardEntity      


class DashboardORMService:


    def get_dashboard(self, uuid: Id) -> DashboardEntity:
        try:
            dashboard_data = DashboardModel.objects.get(uuid=uuid.value)
            dashboard_dict = dashboard_data.get_properties_dict()
            return DashboardEntity.createOf(**dashboard_dict)

        except ObjectDoesNotExist:
            msg = f"Dashboard not found where uuid: {uuid.value}"
            print(msg)
            raise DashboardNotFoundException(msg)
        except Exception as e:
            msg = f"Error: {str(e)}"
            print(msg)
            raise Exception(msg)
        

    def save_dashboard(self, dashboard: DashboardEntity) -> DashboardEntity:
        try:
            dashboard_data, _ = DashboardModel.objects.get_or_create(
                uuid=dashboard.uuid.value,
                user_id=dashboard.user_id,
                description=dashboard.description,
                status=dashboard.status,
                datatables_columns_config=dashboard.datatables_columns_config,
                highcharts_config=dashboard.highcharts_config,
                query=dashboard.query,
                fields=dashboard.fields,
                context=dashboard.context,
                is_public=dashboard.is_public,
                created_at=dashboard.created_at,
            )

            dashboard.set_id(dashboard_data.id)
            return dashboard
        
        except Exception as e:
            msg = f"Error: {str(e)}"
            print(msg)
            raise Exception(msg)