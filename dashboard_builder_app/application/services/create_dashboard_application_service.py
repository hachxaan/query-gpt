# dashboard_builder_app/application/services/chat_proxy_application_service.py



from backoffice.utils import get_session_user
from dashboard_builder_app.domain.repositories.dashboard_repository import IDashboard
from dashboard_builder_app.shared.ddd.domain.model.Id import Id
from dashboard_builder_app.domain.entities.dashboard_entity import DashboardEntity


class CreateDashboardApplicationService:
    def __init__(
            self, 
            dashboard_repository: IDashboard
        ):  
        self.dashboard_repository = dashboard_repository
        self.user = get_session_user()

    def create_dashboard(self) -> dict:


        dashboard = DashboardEntity.createOf(user_id=self.user.id)
        dashboard = dashboard.save()

        return dashboard.to_dict()
    

