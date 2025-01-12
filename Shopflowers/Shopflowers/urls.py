
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
import importlib

views = importlib.import_module('shop.views')



urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('', views.home, name='home'),
    path('order/', views.order, name='order'),

]
