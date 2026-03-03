from django.db import models

# Create your models here.

class AdminLogin(models.Model):   
    email = models.EmailField()
    password = models.CharField(max_length=10,unique=True)