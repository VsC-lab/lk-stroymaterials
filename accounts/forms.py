from django import forms
from .models import Order, OrderItem

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

from django.forms import inlineformset_factory
from .models import Order, OrderItem

# Создаем формсет для позиций заказа
OrderItemFormSet = inlineformset_factory(
    Order, 
    OrderItem, 
    fields=['product', 'quantity', 'price'],
    extra=1,
    can_delete=True
)
from django import forms
from .models import CartItem

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