# dashboard_builder_app/domain/entities/dashboard_entity.py

from datetime import datetime
from dashboard_builder_app.domain.defaults.highcharts import HIGHCHARTS_DEFAULTS
from dashboard_builder_app.shared.ddd.domain.model.EntityRoot import EntityRoot
from dashboard_builder_app.shared.ddd.domain.model.Id import Id


class DashboardEntity(EntityRoot):

    _uuid: Id
    _id: int
    _description: str
    _user_id: int
    _status: str
    _datatables_columns_config: dict
    _highcharts_config: dict
    _query: str
    _fields: list
    _context: dict
    _is_public: bool
    _created_at: datetime

    def __init__(self, **kwargs):
        
        if kwargs.get('id', None):
            data_dashboard = kwargs
        else:
            data_dashboard = self.get_default_data_dashboard(**kwargs)


        self._id = data_dashboard.get('id')
        uuid = data_dashboard.get('uuid')

        if isinstance(uuid, Id):
            self._uuid = uuid
        elif isinstance(uuid, str):
            self._uuid = Id.ofString(uuid)
        else:
            self._uuid = Id.create()
        
        self._description = data_dashboard.get('description')
        self._user_id = kwargs.get('user_id')
        self._status = data_dashboard.get('status')
        self._datatables_columns_config = data_dashboard.get('datatables_columns_config')
        self._highcharts_config = data_dashboard.get('highcharts_config')
        self._query = data_dashboard.get('query')
        self._fields = data_dashboard.get('fields')
        self._context = data_dashboard.get('context')
        self._is_public = data_dashboard.get('is_public')
        self._created_at = data_dashboard.get('created_at')
    
    def get_default_data_dashboard(self, **kwargs) -> dict:
        return {
            'id': None,
            'uuid': Id.create(),
            'description': '',
            'user_id': kwargs.get('user_id'),
            'status': 'pending',
            'datatables_columns_config': {},
            'highcharts_config': HIGHCHARTS_DEFAULTS,
            'query': '',
            'fields': [],
            'context': {},
            'is_public': False,
            'created_at': datetime.now()
        }
    

    @staticmethod
    def createOf(**kwargs) -> 'DashboardEntity':
        dashboard = DashboardEntity(**kwargs)
        return dashboard
    
    def save(self):
        from dashboard_builder_app.domain.events.dashboard_created_event import MainChatSavedEvent
        return EntityRoot.publishEvent(MainChatSavedEvent(self))
   

    def to_dict(self) -> dict:
        dashboard_dict = {
            'id': self.id,
            'uuid': str(self.uuid.value),
            'description': self.description,
            'user_id': self.user_id,
            'status': self.status,
            'datatables_columns_config': self.datatables_columns_config,
            'highcharts_config': self.highcharts_config,
            'query': self.query,
            'fields': self.fields,
            'context': self.context,
            'is_public': self.is_public,
            'created_at': self.created_at
        }

        return dashboard_dict
    
    def set_id(self, id: int):
        self._id = id

    @property
    def id(self) -> int:
        return self._id

    @property
    def uuid(self) -> Id:
        return self._uuid

    @property
    def description(self) -> str:
        return self._description

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def status(self) -> str:
        return self._status

    @property
    def datatables_columns_config(self) -> dict:
        return self._datatables_columns_config

    @property
    def highcharts_config(self) -> dict:
        return self._highcharts_config

    @property
    def query(self) -> str:
        return self._query

    @property
    def fields(self) -> list:
        return self._fields

    @property
    def context(self) -> dict:
        return self._context

    @property
    def is_public(self) -> bool:
        return self._is_public

    @property
    def created_at(self) -> datetime:
        return self._created_at
