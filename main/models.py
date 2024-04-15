from account.models import Account, Company
from ckeditor.fields import RichTextField
from board.models import Lead
from django.db import models
from .tasks import send_to_bot
from django_celery_beat.models import ClockedSchedule, PeriodicTask, PeriodicTasks
from datetime import datetime
import json

class Calendar(models.Model):
    col = (
        ("bg-primary", "Ko'k"),
        ("bg-warning", "Sariq"),
        ("bg-info", "Fiolet"),
        ("bg-success", "Yashil"),
        ("bg-danger", "Qizil")
    )
    user = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True)
    color = models.CharField(choices=col, default="bg-primary", max_length=255)
    event = models.CharField(max_length=255)
    created_user = models.ForeignKey(Account, on_delete=models.CASCADE)
    date = models.DateTimeField()

    def __str__(self):
        return str(self.date)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # print('hhhhhh')
        # print(self.date)
        # send_to_bot.apply_async(args=[self.event])
        text = "Eslatma \n"
        text += f"\nMijoz: {self.user.name}"
        text += f"\nYaratti: {self.created_user.first_name}"
        text += f"\nEslatma: {self.event}"
        clocked_schedule = ClockedSchedule.objects.create(clocked_time=self.date)
        PeriodicTask.objects.create(
            name=f"Message is sending to Telegram Bot: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            clocked=clocked_schedule,
            task="main.tasks.send_to_bot",
            enabled=True,
            one_off=True,
            kwargs=json.dumps({
                "text": text,
                "bot_token": f'{self.created_user.company.bot_token}',
                "group_id": f'{self.created_user.company.group_chat_id}',
                "user_tg_id": f'{self.user.tg_id}'
            }),
        )




    class Meta:
        verbose_name_plural = 'Kalendar'


class Objections(models.Model):
    objection = models.TextField()
    solution = models.TextField()
    create_user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.objection

    class Meta:
        verbose_name_plural = 'Ko`p takrorlanadigan e`tirozlar'


class ObjectionWrite(models.Model):
    objection = models.TextField()
    solution = models.TextField()
    create_user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.objection

    class Meta:
        verbose_name_plural = 'Mijoz e`tirozlari'


class Script(models.Model):
    # company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    text = RichTextField()
    create_user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name_plural = 'Sotuv Transkript'


class Debtors(models.Model):
    create_user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(Lead, on_delete=models.CASCADE)
    summa = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    debt = models.BooleanField()

    def __str__(self):
        return self.user.name

    class Meta:
        verbose_name_plural = 'Qarzdorliklar'


class ImportTemplate(models.Model):
    xlsx = models.FileField(upload_to="template")

    def __str__(self):
        return "Excel"

    class Meta:
        verbose_name_plural = 'Excel'