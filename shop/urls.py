from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.home, name='home'),
    path('shop/', views.shop_catalog, name='shop_catalog'),
    path('search/', views.product_search, name='product_search'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('track/', views.track_order, name='track_order'),
    path('gallery/', views.product_gallery, name='product_gallery'),
    path('filter/', views.category_filter, name='category_filter'),
    path('stock/', views.check_stock, name='check_stock'),
    path('newsletter/', views.newsletter_signup, name='newsletter'),
    path('promo/', views.promo_validator, name='promo'),
    path('staff-login/', views.staff_login_view, name='staff_login'),
]
