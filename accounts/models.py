from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_verified = models.BooleanField(default=False)
    email_token = models.CharField(max_length=50 , null=True , blank=True)
    ip_address = models.CharField(max_length=16 , null=True , blank=True)
