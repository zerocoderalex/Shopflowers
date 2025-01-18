# Shopflowers
webshop
 cart = request.session.get('cart', {})
    action = request.GET.get('action')

    if action == 'increment':
        cart[product_id] = cart.get(product_id, 0) + 1
    elif action == 'decrement':
        if product_id in cart and cart[product_id] > 1:
            cart[product_id] -= 1
        else:
            cart.pop(product_id, None)