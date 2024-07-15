# dashboard_builder_app/domain/repositories/dashboard_repository.py


from abc import ABC, abstractmethod
from dashboard_builder_app.domain.entities.dashboard_entity import DashboardEntity
from dashboard_builder_app.shared.ddd.domain.model.Id import Id

class IDashboard(ABC):

    @abstractmethod
    def get_dashboard(self, uuid: Id) -> DashboardEntity:
        pass


    @abstractmethod
    def save_dashboard(self, dashboard: DashboardEntity) -> DashboardEntity:
        pass