from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings 
from django.conf.urls.static import static 

from chat.views import chatbot_api 

urlpatterns = [
    # Admin Site
    path('admin/', admin.site.urls),
    
    # Rute Aplikasi Utama
    path('auth/', include('users.urls')),
    path('tasks/', include('tasks.urls')), 
    path('documents/', include('documents.urls')),
    path('chat/', include('chat.urls')), 
    path('latihan/', include('latihan.urls')),
    
    # Endpoint API (AJAX)
    path('api/chatbot/', chatbot_api, name='chatbot_api'),
    
    # Internasionalisasi (i18n)
    path('i18n/', include('django.conf.urls.i18n')),
    
    # Redirect URL Root ke Login
    path('', RedirectView.as_view(url='/auth/login/', permanent=False)), 
]

# Konfigurasi file media untuk mode development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)