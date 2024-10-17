#book/urls.py
# Django Imports
from django.urls import path

# Project-Specific Imports
from .views import *

urlpatterns = [
    path('create/',TenantCreateView.as_view()),
]
 