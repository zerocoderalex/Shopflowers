from django import forms
from .models import Order

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['delivery_address', 'products']