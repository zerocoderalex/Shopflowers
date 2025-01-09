from django.urls import path
from .views import  register, catalog, order, home

urlpatterns = [
    path('register/', register, name='register'),
    path('catalog/', catalog, name='catalog'),
    path('order/', order, name='order'),
    path('', home, name='home'),
]