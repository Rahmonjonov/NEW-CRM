from django.db import models
from account.models import Account
# Create your models here.

class Bot(models.Model):
    token = models.CharField(max_length=255)
    admin = models.ForeignKey(Account, on_delete=models.CASCADE)

class BotUpdate(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    last_update = models.IntegerField(default=0)