from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from .forms import UserRegisterForm, OrderForm
from django.contrib import messages
from .models import Product
import requests

TELEGRAM_API_URL = 'https://api.telegram.org/bot<your_bot_token>/sendMessage'

def home(request):
    return render(request, 'shop/home.html')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Вы успешно зарегистрировались!')
            return  redirect('login')
        else:
            messages.error(request, 'Произошла ошибка, проверьте данные.')

    else:
        form = UserRegisterForm()  # Создаем пустую форму для GET-запроса

    return render(request, 'shop/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Вы успешно вошли!')
            return redirect('home')
        else:
            messages.error(request, 'Произошла ошибка, проверьте данные.')
    else:
        form = AuthenticationForm()
    return render(request, 'shop/login.html', {'form': form})


def catalog(request):
    products = Product.objects.all()
    return render(request, 'shop/catalog.html', {'products': products})

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
    return render(request, 'shop/order.html', {'form': form})

def send_telegram_notification(order):
    message = f"Новый заказ:\n" \
              f"Пользователь: {order.user.username}\n" \
              f"Адрес доставки: {order.delivery_address}\n" \
              f"Товары: {', '.join([str(product) for product in order.products.all()])}"
    requests.post(TELEGRAM_API_URL, data={'chat_id': '<your_chat_id>', 'text': message})