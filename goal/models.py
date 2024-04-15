from django.db import models
from account.models import Account

# Create your models here.

class Goal(models.Model):
    user = models.ForeignKey(Account,on_delete=models.CASCADE)
    type = models.CharField(default="Oy",choices=(("Oylik","Oylik"),("Yillik","Yillik")),max_length=25)
    savdo = models.IntegerField(default=0)
    mijoz_soni = models.IntegerField(default=0)
    date = models.DateField(auto_now_add=True)
    oy = models.IntegerField(default=0)
    yil = models.IntegerField(default=0)



