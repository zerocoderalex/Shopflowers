# from aiohttp import request
# from allauth.account.views import email
from django.shortcuts import render, redirect
from django.utils.crypto import get_random_string
from django.contrib.auth.decorators import login_required
from .models import Product, Order, OrderItem, User



def home(request):
    return render(request, 'home.html')


def products(request):
    all_products = Product.objects.all()
    return render(request, 'products.html', {'products': all_products})


def cart(request):
    cart_items = request.session.get('cart', {})
    products = []
    total_price = 0

    for product_id, quantity in cart_items.items():
        product = Product.objects.get(id=product_id)
        products.append({'product': product, 'quantity': quantity, 'total': product.price * quantity})
        total_price += product.price * quantity

    return render(request, 'cart.html', {'products': products, 'total_price': total_price})

def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart
    return redirect('cart')

def update_cart(request, product_id):
    cart = request.session.get('cart', {})
    action = request.GET.get('action')

    if action == 'increment':
        cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    elif action == 'decrement':
        if str(product_id) in cart and cart[str(product_id)] > 1:
            cart[str(product_id)] -= 1
        else:
            cart.pop(str(product_id), None),
    request.session['cart'] = cart
    return redirect('cart')


def order(request):
    cart = request.session.get('cart', {})
    if not cart:
        return render(request, 'order.html', {'message': 'Корзина пуста!'})

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        address = request.POST.get('address')

        if not (full_name and email and address):
            return render(request, 'order.html', {'message': 'Все поля обязательны!'})

        # Создаём пользователя
        users = User.objects.filter(full_name=full_name, email=email, address=address)
        if users.exists():
            user = users.first()  # Берет первого пользователя из QuerySet
        else:
            user = User.objects.create(full_name=full_name, email=email, address=address)

        # Создаём заказ
        order_key = get_random_string(10)
        order = Order.objects.create(user=user, status='pending', order_key=order_key)

        # Добавляем цветы в заказ
        for product_id, quantity in cart.items():
            product = Product.objects.get(id=product_id)
            OrderItem.objects.create(order=order, product=product, quantity=quantity)
            delivery_time = order.delivery_time
            delivery_address = order.delivery_address
        # Очищаем корзину
        request.session['cart'] = {}

        # Передаем дату создания заказа в контекст
        return render(request, 'order.html', {
            'order_key': order_key,
            'created_at': order.created_at,
            'delivery_address': delivery_address,
            'delivery_time': delivery_time,
            'message': 'Заказ успешно оформлен!'
        })

    return render(request, 'order.html')


@login_required
def order_list(request):

    # Получаем текущего пользователя
    current_user = User.objects.get(full_name=request.user)
    # Извлекаем все заказы для этого пользователя
    orders = Order.objects.filter(user=current_user)


    return render(request, 'order_list.html', {'orders': orders})

