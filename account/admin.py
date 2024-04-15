from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from account.models import Account, Company, Invoice, Plan, Card


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'manzil', 'balance', 'plan', 'active', 'type')
    list_display_links = ['name']
    list_filter = ['type']


class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'token', 'phone', 'company')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions', 'is_director'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'company')
    list_display_links = ['username']
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'company')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'company', 'start', 'end', 'summa', 'active', 'timestamp']


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'max_worker_count', 'info', 'price']
    list_display_links = ['id', 'name']


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('id', 'company', 'name', 'number', 'expire', 'active')


admin.site.register(Account, UserAdmin)
admin.site.unregister(Group)
