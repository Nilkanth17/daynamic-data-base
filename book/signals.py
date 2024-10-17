# book/signals.py

# Django Imports
from django.db import connection
from django.db.models.signals import post_save
from django.dispatch import receiver

# Project-Specific Imports
from .models import Tenant


# @receiver(post_save, sender=Tenant)
# def create_dynamic_database(sender, instance, created, **kwargs):
#     if created:
#         db_name = instance.db_name
#         # Create a new database dynamically
#         with connection.cursor() as cursor:
#             cursor.execute(f"CREATE DATABASE \"{db_name}\";")
#         print(f"Database {db_name} created successfully!")

