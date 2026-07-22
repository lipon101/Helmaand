from django.contrib import admin
from .models import CTFFlag


@admin.register(CTFFlag)
class CTFFlagAdmin(admin.ModelAdmin):
    list_display = ['challenge_id', 'flag', 'category', 'difficulty']
    list_filter = ['category', 'difficulty']
    search_fields = ['challenge_id', 'flag']
