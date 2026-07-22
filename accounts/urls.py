from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('change-email/', views.change_email_view, name='change_email'),
    path('reset-preferences/', views.reset_preferences_view, name='reset_preferences'),
    path('quick-login/', views.quick_login_view, name='quick_login'),
    path('force-logout/', views.force_logout_view, name='force_logout'),
    path('change-password/', views.change_password_view, name='change_password'),
]
