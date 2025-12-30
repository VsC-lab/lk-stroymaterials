# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Order, OrderItem, CartItem


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['delivery_address', 'comments']
        widgets = {
            'delivery_address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }
        labels = {
            'delivery_address': 'Адрес доставки',
            'comments': 'Комментарии к заказу',
        }


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }


# Создаем формсет для позиций заказа
from django.forms import inlineformset_factory

OrderItemFormSet = inlineformset_factory(
    Order, 
    OrderItem, 
    form=OrderItemForm,
    fields=['product', 'quantity'],
    extra=1,
    can_delete=True
)


class CartItemForm(forms.ModelForm):
    """Форма для изменения количества товара в корзине"""
    class Meta:
        model = CartItem
        fields = ['quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 100,
                'style': 'width: 80px;'
            })
        }