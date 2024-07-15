# dashboard_builder_app/domain/entities/classifier_entity.py


from typing import Dict
from dashboard_builder_app.shared.ddd.domain.model.EntityRoot import EntityRoot


class ClassifierEntity(EntityRoot):

    promt_template: str
    model: str
    uuid: str

    chat_id: int
    message_json: Dict


    def __init__(self, **kwargs):
        self.promt_template = kwargs.get('promt_template')
        self.model = kwargs.get('model')
        self.uuid = kwargs.get('uuid')


    @staticmethod
    def createOf(**kwargs) -> 'ClassifierEntity':
        classifier = ClassifierEntity(**kwargs)
        return classifier