from django import forms
from .models import Order
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

        def save(self, commit=True):
            user = super().save(commit=False)
            user.password = make_password(self.cleaned_data['password'])  # Хеширование пароля
            if commit:
                user.save()
            return user

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['delivery_address', 'products']