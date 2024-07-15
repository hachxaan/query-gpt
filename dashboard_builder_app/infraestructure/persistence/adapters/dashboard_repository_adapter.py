# dashboard_builder_app/infraestructure/persistence/adapters/dashboard_repository_adapter.py


from dashboard_builder_app.domain.entities.dashboard_entity import DashboardEntity
from dashboard_builder_app.domain.repositories.dashboard_repository import IDashboard
from dashboard_builder_app.infraestructure.persistence.services.dashboard_orm_service import DashboardORMService
from dashboard_builder_app.shared.ddd.domain.model.Id import Id

class DashboaradRespositoryAdapter(IDashboard):

    def __init__(self, dashboard_orm_service: DashboardORMService):
        self.dashboard_orm_service = dashboard_orm_service

    def get_dashboard(self, uuid: Id) -> DashboardEntity:
        return self.dashboard_orm_service.get_dashboard(uuid=uuid)
    

    def save_dashboard(self, dashboard: DashboardEntity) -> DashboardEntity:
        return self.dashboard_orm_service.save_dashboard(dashboard=dashboard)
 