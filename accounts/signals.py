# accounts/signals.py
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.db import transaction
from django.utils.timezone import now

try:
    from .cart_utils import merge_carts, get_or_create_cart
    from .models import Cart, CartItem
    CART_AVAILABLE = True
except ImportError:
    CART_AVAILABLE = False
    print("⚠️ cart_utils не найден, функции корзины недоступны")

@receiver(user_logged_in)
def handle_user_login(sender, request, user, **kwargs):
    """
    Обработчик входа пользователя
    """
    print(f"✅ Пользователь {user.username} вошел в систему")
    
    # Обновляем last_login (можно добавить свои поля)
    user.last_login = now()
    user.save(update_fields=['last_login'])
    
    # Объединяем корзины если доступно
    if CART_AVAILABLE:
        try:
            # Получаем ключ сессии
            session_key = request.session.session_key
            
            # Ищем гостевую корзину
            session_cart = None
            if session_key:
                session_cart = Cart.objects.filter(
                    session_key=session_key,
                    user__isnull=True
                ).first()
            
            # Получаем или создаем корзину пользователя
            user_cart, created = Cart.objects.get_or_create(user=user)
            
            # Объединяем если есть что объединять
            if session_cart and session_cart.items.exists():
                merge_carts(session_cart, user_cart)
                print(f"🛒 Корзины объединены для {user.username}")
                
                # Обновляем сессию
                if 'cart_id' in request.session:
                    del request.session['cart_id']
        except Exception as e:
            print(f"❌ Ошибка при объединении корзин: {e}")

@receiver(user_logged_out)
def handle_user_logout(sender, request, user, **kwargs):
    """
    Обработчик выхода пользователя
    """
    if user:
        print(f"✅ Пользователь {user.username} вышел из системы")
    else:
        print("✅ Анонимный пользователь вышел из системы")