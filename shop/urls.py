from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.home, name='home'),
    path('shop/', views.shop_catalog, name='shop_catalog'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
]