from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import RegistrationForm, OrderForm
from .models import Product
import requests

TELEGRAM_API_URL = 'https://api.telegram.org/bot<your_bot_token>/sendMessage'

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            use
r = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('catalog')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def catalog(request):
    products = Product.objects.all()
    return render(request, 'catalog.html', {'products': products})

def order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            order.products.set(form.cleaned_data['products'])
            order.save()
            send_telegram_notification(order)
            return redirect('catalog')
    else:
        form = OrderForm()
    return render(request, 'order.html', {'form': form})

def send_telegram_notification(order):
    message = f"Новый заказ:\n" \
              f"Пользователь: {order.user.username}\n" \
              f"Адрес доставки: {order.delivery_address}\n" \
              f"Товары: {', '.join([str(product) for product in order.products.all()])}"
    requests.post(TELEGRAM_API_URL, data={'chat_id': '<your_chat_id>', 'text': message})