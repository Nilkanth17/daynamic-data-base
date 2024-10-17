# dynamic/routers.py
class DynamicDBRouter:
    """
    A router to control database operations on certain models or apps.
    """

    def db_for_read(self, model, **hints):
        # Use the dynamic database for reads
        return 'dynamic_db'

    def db_for_write(self, model, **hints):
        # Use the dynamic database for writes
        return 'dynamic_db'

    def allow_relation(self, obj1, obj2, **hints):
        # Allow any relations if both objects are in the same database
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Allow migrations only on the default database
        if db == 'dynamic_db':
            return True
        return None
