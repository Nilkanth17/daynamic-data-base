# book/views.py

# Django Imports
from django.conf import settings
from django.core.management import call_command

# Django REST Framework Imports
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# Project-Specific Imports
from book.models import Tenant
from .utils import set_dynamic_db

import psycopg2

class TenantCreateView(APIView):
    def post(self, request):
        name = request.data.get('name')
        db_name = request.data.get('db_name')

        # print(f"Creating tenant: {name}, Database: {db_name}")

        connection = None
        tenant_connection = None

        try:
            # Connect to the default database
            connection = psycopg2.connect(
                dbname=settings.DATABASES['default']['NAME'],
                user=settings.DATABASES['default']['USER'],
                password=settings.DATABASES['default']['PASSWORD'],
                host=settings.DATABASES['default']['HOST'],
                port=settings.DATABASES['default']['PORT']
            )
            
            connection.autocommit = True

            # Check if the database already exists
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = %s;", (db_name,))
                exists = cursor.fetchone()

                if exists:
                    return Response({
                        "status": 'faild',
                        "message": f"Database '{db_name}' already exists."
                    }, status=status.HTTP_400_BAD_REQUEST)

            # Create the database
            with connection.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE \"{db_name}\";")
                # print(f"Database '{db_name}' created successfully.")

            set_dynamic_db(db_name)

            call_command('migrate', database='dynamic_db', interactive=False, verbosity=0)
            # print(f"Migrations applied to database '{db_name}' successfully.")

            Tenant.objects.using('default').create(name=name, db_name=db_name)
            # print("Tenant record created successfully in the default database.")

            return Response({
                "status": 'success',
                "message": "Tenant created successfully.",
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            # print(f"Error: {str(e)}")  
            return Response({
                "status": 'faild',
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        finally:
            if connection:
                connection.close()
            if tenant_connection:
                tenant_connection.close()
    
    def get(self, request):
        tenants = Tenant.objects.using('default').all()
        tenant_list = [{'id': tenant.pk,"name": tenant.name, "db_name": tenant.db_name} for tenant in tenants]
        
        return Response({
            "status": 'success',
            'message': 'data fetched successfully',
            "data": tenant_list
        }, status=status.HTTP_200_OK)

    def put(self, request):
        try:
            pk = request.data.get('pk')
            tenant = Tenant.objects.using('default').get(pk=pk)
            new_name = request.data.get('name')
            new_db_name = request.data.get('db_name')

            if new_name:
                tenant.name = new_name
                
            if new_db_name:
                connection = psycopg2.connect(
                    dbname=settings.DATABASES['default']['NAME'],
                    user=settings.DATABASES['default']['USER'],
                    password=settings.DATABASES['default']['PASSWORD'],
                    host=settings.DATABASES['default']['HOST'],
                    port=settings.DATABASES['default']['PORT']
                )
                connection.autocommit = True
                
                with connection.cursor() as cursor:
                    cursor.execute(f"""
                        SELECT pg_terminate_backend(pg_stat_activity.pid)
                        FROM pg_stat_activity
                        WHERE pg_stat_activity.datname = '{tenant.db_name}' AND pid <> pg_backend_pid();
                    """)

                    cursor.execute(f"ALTER DATABASE \"{tenant.db_name}\" RENAME TO \"{new_db_name}\";")
                    
                tenant.db_name = new_db_name
            
            tenant.save(using='default')

            return Response({
                "status": 'success',
                "message": "Tenant updated successfully."
            }, status=status.HTTP_200_OK)

        except Tenant.DoesNotExist:
            return Response({
                "status": 'faild',
                "message": "Tenant not found."
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "status": 'faild',
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            if connection:
                connection.close()

    def delete(self, request):
        try:
            pk = request.data.get('pk')
            tenant = Tenant.objects.using('default').get(pk=pk)

            connection = psycopg2.connect(
                dbname=settings.DATABASES['default']['NAME'],
                user=settings.DATABASES['default']['USER'],
                password=settings.DATABASES['default']['PASSWORD'],
                host=settings.DATABASES['default']['HOST'],
                port=settings.DATABASES['default']['PORT']
            )
            connection.autocommit = True

            with connection.cursor() as cursor:
                cursor.execute(f"""
                    SELECT pg_terminate_backend(pid)
                    FROM pg_stat_activity
                    WHERE datname = %s AND pid <> pg_backend_pid();
                """, (tenant.db_name,))

            with connection.cursor() as cursor:
                cursor.execute(f"DROP DATABASE \"{tenant.db_name}\";")

            tenant.delete(using='default')

            return Response({
                "status": 'success',
                "message": "Tenant deleted successfully."
            }, status=status.HTTP_200_OK)

        except Tenant.DoesNotExist:
            return Response({
                "status": 'faild',
                "message": "Tenant not found."
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "status": 'faild',
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            if connection:
                connection.close()

