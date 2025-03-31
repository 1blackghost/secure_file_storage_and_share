from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.db import models

class User(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  

    def __str__(self):
        return self.email

class Uploads(models.Model):
    name = models.CharField(max_length=255)
    filename = models.CharField(max_length=255)

    def __str__(self):
        return self.email

class Send_Data(models.Model):
    name = models.CharField(max_length=255)
    filename = models.CharField(max_length=255)
    receiver = models.CharField(max_length=255)
    request = models.CharField(max_length=2,default=0)
    done = models.CharField(max_length=2,default=0)

    def __str__(self):
        return self.email