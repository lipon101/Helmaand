from django.contrib import admin
from .models import Category, Product, ProductImage, Review, Promo
from django.utils.safestring import mark_safe


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'is_active', 'created_at']
    list_filter = ['category', 'is_active']
    list_editable = ['price', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'brand']


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'alt_text']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at']
    list_filter = ['rating']
    search_fields = ['comment', 'user__username']


@admin.register(Promo)
class PromoAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['code']
