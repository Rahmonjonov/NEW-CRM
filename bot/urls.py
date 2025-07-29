from django.urls import path
from .views import *

urlpatterns = [
    path('add_bot',add_bot, name='add_bot'),
    path('telegram_webhook',telegram_webhook, name='telegram_webhook'),

]
