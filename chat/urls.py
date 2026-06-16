from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_view, name='chat_view'), 
    
    path('api/chatbot/', views.chatbot_api, name='chatbot_api'),
    path('api/history/<int:sesi_id>/', views.get_chat_history_api, name='get_history'),
    path('api/delete/<int:sesi_id>/', views.delete_chat_session_api, name='delete_chat_session_api'),
]