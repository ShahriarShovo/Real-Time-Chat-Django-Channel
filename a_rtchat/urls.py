from django.urls import path
from a_rtchat.views import chat_view

urlpatterns = [
    path('', chat_view, name='home'),
]
