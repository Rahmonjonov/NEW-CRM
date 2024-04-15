from django.contrib import admin
from django_celery_beat.models import ClockedSchedule, PeriodicTask, PeriodicTasks
from main.models import ImportTemplate, Script, Objections, ObjectionWrite, Calendar, Debtors

admin.site.register(ImportTemplate)
# admin.site.register(PeriodicTask)
# admin.site.register(ClockedSchedule)


@admin.register(Script)
class ScriptAdmin(admin.ModelAdmin):
    list_display = ('id', 'text')
    list_display_links = ('id', 'text')


@admin.register(Objections)
class ObjectionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'objection', 'solution')


@admin.register(ObjectionWrite)
class ObjectionWriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'objection', 'solution')


@admin.register(Calendar)
class CalendarAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'date')
    list_display_links = ('id', 'event', 'date')


@admin.register(Debtors)
class DebtorsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'summa', 'date')
    list_display_links = ('id', 'user', 'summa', 'date')
