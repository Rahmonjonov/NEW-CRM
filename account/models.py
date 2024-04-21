from django.contrib.auth.models import AbstractUser
from django.db import models

Company_default_poles = [
    ("Boshlang'ich", 0),
    ("Muhokamada", 1),
    ("Qaror qabul qilish", 2),
    ("Shartnoma", 3)
]

Company_type_choise = (
    ("B2C", "Biznesdan mijozga (B2C)"),
    ("B2B", "Biznesdan biznesga (B2B)")
)


class Plan(models.Model):
    name = models.CharField(max_length=255)
    max_worker_count = models.IntegerField(default=0)
    info = models.TextField(default="")
    price = models.BigIntegerField(default=0)
    is_trial = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return self.name


class Company(models.Model):
    logo = models.ImageField(upload_to='logos')
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=25)
    manzil = models.CharField(max_length=255)
    creator = models.CharField(max_length=255, null=True, blank=True)
    about = models.TextField(null=True)

    tg_token = models.TextField(null=True)

    bot_token = models.TextField(null=True)
    group_chat_id = models.TextField(null=True)

    balance = models.BigIntegerField(default=0)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, default=None)
    active = models.BooleanField(default=False)
    type = models.CharField(max_length=3, choices=Company_type_choise, default="B2C")

    # eskiz
    sms_email = models.CharField(max_length=255, null=True, blank=True)
    sms_password = models.CharField(max_length=255, null=True, blank=True)
    sms_token = models.TextField(null=True)
    sms_balans = models.IntegerField(default=0)
    sms_from = models.CharField(max_length=255, null=True, blank=True)
    sms_callback_url = models.CharField(max_length=255, null=True, blank=True)
    sms_activated = models.BooleanField(default=False)

    smsto_client_id = models.CharField(max_length=255, null=True, blank=True)
    smsto_secret = models.CharField(max_length=255, null=True, blank=True)
    smsto_expires_in = models.IntegerField(default=600000)
    smsto_token = models.TextField(null=True)
    smsto_sender_id = models.CharField(max_length=11, null=True, blank=True)
    smsto_activated = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Invoice(models.Model):
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True)
    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True)
    summa = models.BigIntegerField(default=0)
    active = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)


class Account(AbstractUser):
    is_director = models.BooleanField(default=False)
    is_influencer = models.BooleanField(default=False)
    token = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=25, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'

    def save(self, *args, **kwargs):
        if self.company:
            count = Account.objects.filter(company=self.company).count()
            self.company.worker_count = count
            self.company.save()
        super(Account, self).save(*args, **kwargs)


class Card(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    number = models.CharField(max_length=30)
    expire = models.CharField(max_length=10)
    active = models.BooleanField(default=False)
    token = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
