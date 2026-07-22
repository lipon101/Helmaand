from django.urls import path
from django.shortcuts import render
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.Profile, name='profile'),  # <--- Capital 'P'
]
def admin_dashboard(request):
    return render(request, 'dashboard/admin_dashboard.html')  # or render whatever dashboard template you have