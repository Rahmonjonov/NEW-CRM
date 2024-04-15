from django.contrib import admin
from .models import *
# Register your models here.
#
@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ['id','user','savdo','mijoz_soni','oy','yil','date']