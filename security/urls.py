from django.urls import path
from django.http import HttpResponse

app_name = 'security'

urlpatterns = [
    path('lab/', lambda r: HttpResponse("Security Lab"), name='lab_index'),
]