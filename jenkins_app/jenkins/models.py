from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class Developer(AbstractUser):
    developer_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=20,blank=False,null=False,unique=True)
    password = models.CharField(max_length=500,blank=False,null=False)
    build_token = models.CharField(max_length=100,blank=True,null=True)
    jenkins_username = models.CharField(max_length=50,blank=True,null=True)
    created = models.DateTimeField(auto_now_add=True)

class PushNotification(models.Model):
    developer = models.OneToOneField(Developer,on_delete=models.CASCADE,blank=False,null=False)
    notification_token = models.CharField(max_length=1000,blank=True,null=True)