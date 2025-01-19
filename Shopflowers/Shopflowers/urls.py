
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
import shop.views as views



urlpatterns = [
    path('admin/', admin.site.urls),
    path('cart/', views.cart, name='cart'),
    path('', views.home, name='home'),
    path('order/', views.order, name='order'),
    path('products/', views.products, name='products'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/<int:product_id>/', views.update_cart, name='update_cart'),
    path('accounts/', include('allauth.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



