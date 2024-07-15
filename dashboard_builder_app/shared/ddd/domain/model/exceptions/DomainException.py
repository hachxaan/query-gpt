from .DomainExceptionTags import ERRORS


class DomainException(Exception):
    def __init__(self, tag=None, message=None):
        self.tag = tag
        self.message = message

        if self.tag in ERRORS:
            self.__set_properties(ERRORS[tag], message)
        else:
            self.__set_properties(ERRORS['INTERNAL_ERROR'], message)

    def __set_properties(self, error, message):
        self.message = error['message']
        self.code = error['code']

        if message is not None:
            self.message = message

    @property
    def serialize(self):
        return {
            'code': self.code,
            'tag': self.tag,
            'message': self.message
        }
