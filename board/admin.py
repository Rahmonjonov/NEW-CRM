from django.contrib import admin
from board.models import *

@admin.register(NewComplaints)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('id', 'complaint')

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')


@admin.register(Instruktsya)
class InstruktsyaAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'company')
    list_display_links = ('id', 'title')
    list_filter = ['company']

@admin.register(LeadPoles)
class LeadStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'company', 'status')
    list_display_links = ('id', 'name')
    list_filter = ['company']

@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'region')
    list_display_links = ('id', 'name')
    list_filter = ('region',)


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'price', 'company', 'companyAddress', 'status', 'pole', 'date', 'created_user',
                    'phone', 'is_active', 'created_user']
    list_filter = ['created_user__company', 'status', 'pole']
    list_display_links = ['id', 'name']
    search_fields = ['name', 'phone']

    # def get_queryset(self, request):
    #     qs = super(LeadAdmin, self).get_queryset(request)
    #     if not request.user.is_superuser:
    #         return qs
    #     return qs.filter(company=request.user.company)


@admin.register(LeadAction)
class LeadActionAdmin(admin.ModelAdmin):
    list_display = ['id', 'lead', 'status', 'oldStatus', 'newStatus', 'date', 'note', 'changer']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'note', 'status', 'date', 'finishedDate', 'created_user']
    list_filter = ['created_user__company', 'status']
    search_fields = ['name']


@admin.register(Telegram_user)
class Telegram_userAdmin(admin.ModelAdmin):
    list_display = ['id', 'chat_id', 'name', 'company', 'companyAddress', 'phone', 'step']
    search_fields = ['chat_id']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'company', 'name', 'price', 'comment']
    list_filter = ['company']


@admin.register(Payment_type)
class Payment_typeAdmin(admin.ModelAdmin):
    list_display = ['id', 'company', 'name']
    list_filter = ['company']


@admin.register(SMSTemplate)
class SMSTemplateAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at', 'company', 'name', 'type', 'date', 'active']
    list_filter = ['company', 'type', 'active']


@admin.register(SMSHistory)
class SMSHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'smstemplate', 'created_at', 'date', 'is_success', 'send_count', 'not_send_count']
    list_filter = ['smstemplate__company', 'is_success']


@admin.register(UrlRedirect)
class UrlRedirectAdmin(admin.ModelAdmin):
    list_display = ['id', 'company', 'date', 'name', 'next_url', 'total_count', 'telegram_count', 'instagram_count',
                    'facebook_count', 'youtube_count', 'tiktok_count', 'telegram_url', 'instagram_url', 'facebook_url',
                    'youtube_url', 'tiktok_url']
    list_display_links = ['id', 'name']
    list_filter = ['company']


@admin.register(NoteForm)
class NoteFormAdmin(admin.ModelAdmin):
    list_display = ['id', 'company', 'date', 'name', 'total_count', 'telegram_count', 'instagram_count',
                    'facebook_count', 'youtube_count', 'tiktok_count', 'telegram_url', 'instagram_url', 'facebook_url',
                    'youtube_url', 'tiktok_url']
    list_display_links = ['id', 'name']
    list_filter = ['company']


@admin.register(FormQuestion)
class FormQuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'form', 'name']
    list_display_links = ['id', 'name']
    list_filter = ['form__company']


@admin.register(FormAnswer)
class FormAnswerAdmin(admin.ModelAdmin):
    list_display = ['id', 'form', 'date', 'join_by']
    list_display_links = ['id', 'form']
    list_filter = ['form__company']


@admin.register(AnswerQuestion)
class AnswerQuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'question', 'text', 'answer']
    list_display_links = ['id', 'text']
    list_filter = ['question__form__company']


@admin.register(Shopping)
class ShoppingAdmin(admin.ModelAdmin):
    list_display = ['id', 'company', 'date', 'lead', 'product', 'count', 'price', 'amount', 'account', 'payment_type']
    list_display_links = ['id', 'company']
    list_filter = ['company']
