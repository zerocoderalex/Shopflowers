from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import RegistrationForm, OrderForm
from .models import Product
import requests

TELEGRAM_API_URL = 'https://api.telegram.org/bot<your_bot_token>/sendMessage'

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Получаем данные из формы
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            email = form.cleaned_data.get('email')
            # Создаем нового пользователя
            user = User.objects.create_user(username=username, password=password, email=email)
            user.save()  # Сохраняем пользователя в базе данных

            messages.success(request, 'Вы успешно зарегистрировались!')
            return redirect('login')  # Перенаправляем на страницу входа или другую страницу
        else:
            form = RegistrationForm()  # Создаем пустую форму для GET-запроса

        return render(request, 'registration/register.html', {'form': form})


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