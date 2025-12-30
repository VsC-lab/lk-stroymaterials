from .models import Cart, CartItem, Product
from django.db import transaction

def get_or_create_cart(request):
    """
    Получить или создать корзину для пользователя или сессии
    """
    cart = None
    
    if request.user.is_authenticated:
        # Для авторизованных пользователей
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        # Для гостей - используем сессию
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        cart, created = Cart.objects.get_or_create(
            session_key=session_key,
            user=None
        )
    
    return cart

def add_to_cart(request, product_id, quantity=1):
    """
    Добавить товар в корзину
    """
    try:
        product = Product.objects.get(id=product_id, stock__gt=0)
    except Product.DoesNotExist:
        return False, "Товар не найден или отсутствует на складе"
    
    if quantity > product.stock:
        return False, f"Недостаточно товара на складе. Доступно: {product.stock}"
    
    cart = get_or_create_cart(request)
    
    with transaction.atomic():
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            # Если товар уже в корзине, увеличиваем количество
            new_quantity = cart_item.quantity + quantity
            if new_quantity <= product.stock:
                cart_item.quantity = new_quantity
                cart_item.save()
            else:
                return False, f"Нельзя добавить больше {product.stock} единиц товара"
    
    return True, "Товар добавлен в корзину"

def remove_from_cart(request, item_id):
    """
    Удалить позицию из корзины
    """
    try:
        cart = get_or_create_cart(request)
        item = CartItem.objects.get(id=item_id, cart=cart)
        item.delete()
        return True, "Товар удален из корзины"
    except CartItem.DoesNotExist:
        return False, "Товар не найден в корзине"

def update_cart_item(request, item_id, quantity):
    """
    Обновить количество товара в корзине
    """
    try:
        cart = get_or_create_cart(request)
        item = CartItem.objects.get(id=item_id, cart=cart)
        
        if quantity <= 0:
            item.delete()
            return True, "Товар удален из корзины"
        
        if quantity > item.product.stock:
            return False, f"Недостаточно товара на складе. Доступно: {item.product.stock}"
        
        item.quantity = quantity
        item.save()
        return True, "Количество обновлено"
    except CartItem.DoesNotExist:
        return False, "Товар не найден в корзине"

def get_cart_items_count(request):
    """
    Получить количество товаров в корзине для отображения в навигации
    """
    cart = get_or_create_cart(request)
    return cart.total_items

def clear_cart(request):
    """
    Очистить корзину
    """
    cart = get_or_create_cart(request)
    cart.items.all().delete()
    return True, "Корзина очищена"

def merge_carts(session_cart, user_cart):
    """
    Объединить гостевую корзину с пользовательской при входе
    """
    if session_cart and user_cart:
        for session_item in session_cart.items.all():
            user_item, created = user_cart.items.get_or_create(
                product=session_item.product,
                defaults={'quantity': session_item.quantity}
            )
            if not created:
                # Если товар уже есть в пользовательской корзине, суммируем количество
                total_quantity = user_item.quantity + session_item.quantity
                if total_quantity <= session_item.product.stock:
                    user_item.quantity = total_quantity
                    user_item.save()
        
        # Удаляем гостевую корзину
        session_cart.delete()
    
    return user_cart
def merge_carts_on_login(request, user):
    """
    Функция для signals.py - объединяет корзины при входе
    """
    try:
        # Получаем ключ сессии
        session_key = request.session.session_key
        
        # Ищем гостевую корзину
        session_cart = None
        if session_key:
            from .models import Cart
            session_cart = Cart.objects.filter(
                session_key=session_key,
                user__isnull=True
            ).first()
        
        # Получаем или создаем корзину пользователя
        user_cart, created = Cart.objects.get_or_create(user=user)
        
        # Объединяем если есть что объединять
        if session_cart:
            return merge_carts(session_cart, user_cart)
        return user_cart
        
    except Exception as e:
        print(f"Ошибка в merge_carts_on_login: {e}")
        return None