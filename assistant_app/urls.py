from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('voice-assistant-api/', views.voice_assistant_api, name='voice_assistant_api'),
]
