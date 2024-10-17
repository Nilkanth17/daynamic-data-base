# book/models.py

# Create your models here.
from django.db import models

class Tenant(models.Model):
    name = models.CharField(max_length=255)
    db_name = models.CharField(max_length=255, unique=True) 
    
    def __str__(self):
        return self.name
