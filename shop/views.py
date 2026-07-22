from django.shortcuts import render, get_object_or_404
from .models import Product, Category

def home(request):
    featured_products = Product.objects.filter(is_active=True)[:6]
    categories = Category.objects.all()
    return render(request, 'shop/home.html', {
        'featured_products': featured_products,
        'categories': categories
    })

def shop_catalog(request):
    products = Product.objects.filter(is_active=True)
    return render(request, 'shop/catalog.html', {'products': products})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, 'shop/detail.html', {'product': product})
