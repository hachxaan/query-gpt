# backoffice/subcribers_registers.py

def register_subscribers():
    from dashboard_builder_app.application.subscibers.dashboard_created_subscriber import DashboardCreatedSubscriber
    from dashboard_builder_app.infraestructure.persistence.adapters.dashboard_repository_adapter import DashboaradRespositoryAdapter
    from dashboard_builder_app.infraestructure.persistence.services.dashboard_orm_service import DashboardORMService
    from dashboard_builder_app.shared.ddd.domain.model.DomainEventPublisher import DomainEventPublisher

    subscriber = DashboardCreatedSubscriber(dashboard_repository=DashboaradRespositoryAdapter(DashboardORMService()))
    DomainEventPublisher.of().subscribe(subscriber)
