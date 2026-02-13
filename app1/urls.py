from django.urls import path
from .views import kkk, home

urlpatterns = [
    path('', kkk, name='kkk'),
    path('home/', home, name='home'),
]
