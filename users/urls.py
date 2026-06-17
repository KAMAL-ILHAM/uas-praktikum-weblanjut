from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    # Autentikasi Dasar
    path('login/', views.login_view, name='login'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Panel Pengguna
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('tasks/', views.task_list_view, name='task_list'),
    path('settings/', views.settings_view, name='settings'),

    # Alur Reset Password
    path(
        'reset_password/', 
        auth_views.PasswordResetView.as_view(
            template_name="users/reset_password.html", 
            success_url='/auth/reset_password_sent/',
            email_template_name="users/password_reset_email.txt",      
            html_email_template_name="users/password_reset_email.html", 
            subject_template_name="users/password_reset_subject.txt"
        ), 
        name="reset_password"
    ),

    path(
        'reset_password_sent/', 
        auth_views.PasswordResetDoneView.as_view(
            template_name="users/password_reset_sent.html"
        ), 
        name="password_reset_done"
    ),
    path(
        'reset/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(
            template_name="users/password_reset_form.html", 
            success_url='/auth/reset_password_complete/'
        ), 
        name="password_reset_confirm"
    ),
    path(
        'reset_password_complete/', 
        auth_views.PasswordResetCompleteView.as_view(
            template_name="users/password_reset_complete.html"
        ), 
        name="password_reset_complete"
    ),
]