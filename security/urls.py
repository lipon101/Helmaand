from django.urls import path
from . import views

app_name = 'security'

urlpatterns = [
    path('', views.lab_index, name='lab_index'),
    path('vault/', views.vault_view, name='vault'),
]
