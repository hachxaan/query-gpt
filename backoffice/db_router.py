class AppRouter:
    app_label_to_db = {
        'query_builder_app': 'query_builder_app_db',
        'campaign_manager_app': 'campaign_manager_app_db',
        'dashboard_builder_app': 'dashboard_builder_app_db',
    }

    def db_for_read(self, model, **hints):
        return self.app_label_to_db.get(model._meta.app_label, 'default')

    def db_for_write(self, model, **hints):
        return self.app_label_to_db.get(model._meta.app_label, 'default')

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label in self.app_label_to_db or obj2._meta.app_label in self.app_label_to_db:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return db == self.app_label_to_db.get(app_label, 'default')
