from django.urls import path
from .views import *



urlpatterns = [
    path('', chat_view, name='ai_chat'),
    path('send/', chat_send, name='ai_send'),
    path('ai/audio/', analyze_audio_view, name='analyze_audio'),

]