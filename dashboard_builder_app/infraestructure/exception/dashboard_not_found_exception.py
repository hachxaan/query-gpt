# dashboard_builder_app/infraestructure/exception/dashboard_not_found_exception.py

class DashboardNotFoundException(Exception):

    def __init__(self, message=None):
        self.message = message
