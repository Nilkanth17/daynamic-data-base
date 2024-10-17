# utils.py

# Django Imports
from django.conf import settings
from django.db import connections

def set_dynamic_db(db_name):
    """
    Switch to the dynamic database by changing the 'dynamic_db' settings.
    """
    # Ensure that the database name is provided
    if not db_name:
        raise ValueError("Database name must be provided.")

    settings.DATABASES['dynamic_db']['NAME'] = db_name
    connections['dynamic_db'].close()  # Close existing connections