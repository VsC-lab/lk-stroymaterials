from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.http import JsonResponse
from .models import Order, Product, OrderItem, Cart, CartItem
from .forms import OrderForm, OrderItemFormSet, CartItemForm
from .cart_utils import (
    get_or_create_cart, add_to_cart, remove_from_cart, 
    update_cart_item, get_cart_items_count, clear_cart, merge_carts
)

# Главная страница
def home(request):
    products = Product.objects.filter(stock__gt=0)[:8]  # 8 товаров в наличии
    return render(request, 'accounts/home.html', {
        'products': products,
        'user': request.user
    })

# Личный кабинет
@login_required
def dashboard(request):
    user_orders = Order.objects.filter(user=request.user)
    
    stats = {
        'total_orders': user_orders.count(),
        'total_spent': user_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
        'active_orders': user_orders.exclude(status__in=['delivered', 'cancelled']).count(),
    }
    
    recent_orders = user_orders[:5]
    
    return render(request, 'accounts/dashboard.html', {
        'stats': stats,
        'recent_orders': recent_orders,
        'user': request.user
    })

# Список заказов пользователя
@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/order_list.html', {'orders': orders})

# Детали заказа
@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'accounts/order_detail.html', {'order': order})

# Создание нового заказа
@login_required
def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            messages.success(request, f'Заказ {order.order_number} создан!')
            return redirect('order_detail', order_id=order.id)
    else:
        form = OrderForm()
    
    # Товары для выбора
    products = Product.objects.filter(stock__gt=0)
    
    return render(request, 'accounts/create_order.html', {
        'form': form,
        'products': products
    })

# Каталог товаров
def product_catalog(request):
    products = Product.objects.filter(stock__gt=0)
    categories = {}
    
    for product in products:
        if product.category not in categories:
            categories[product.category] = []
        categories[product.category].append(product)
    
    return render(request, 'accounts/catalog.html', {'categories': categories})

# Корзина покупок - просмотр
def cart_view(request):
    cart = get_or_create_cart(request)
    items = cart.items.all()
    
    # Формы для изменения количества
    item_forms = {}
    for item in items:
        item_forms[item.id] = CartItemForm(instance=item)
    
    return render(request, 'accounts/cart.html', {
        'cart': cart,
        'items': items,
        'item_forms': item_forms,
    })

# Добавить товар в корзину
def add_to_cart_view(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        success, message = add_to_cart(request, product_id, quantity)
        
        # Всегда возвращаем JSON если это AJAX запрос
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            cart_count = get_cart_items_count(request)
            return JsonResponse({
                'success': success,
                'message': message,
                'cart_count': cart_count
            })
        else:
            if success:
                messages.success(request, message)
            else:
                messages.error(request, message)
            return redirect('catalog')
    
    return redirect('catalog')

# Удалить товар из корзины
def remove_from_cart_view(request, item_id):
    if request.method == 'POST':
        success, message = remove_from_cart(request, item_id)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # AJAX запрос
            cart_count = get_cart_items_count(request)
            return JsonResponse({
                'success': success,
                'message': message,
                'cart_count': cart_count
            })
        else:
            if success:
                messages.success(request, message)
            else:
                messages.error(request, message)
    
    return redirect('cart_view')

# Обновить количество товара в корзине
def update_cart_item_view(request, item_id):
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
            success, message = update_cart_item(request, item_id, quantity)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # AJAX запрос
                cart_count = get_cart_items_count(request)
                return JsonResponse({
                    'success': success,
                    'message': message,
                    'cart_count': cart_count
                })
            else:
                if success:
                    messages.success(request, message)
                else:
                    messages.error(request, message)
        except ValueError:
            messages.error(request, "Неверное количество")
    
    return redirect('cart_view')

# Очистить корзину
def clear_cart_view(request):
    if request.method == 'POST':
        success, message = clear_cart(request)
        
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
    
    return redirect('cart_view')

# Оформить заказ из корзины
@login_required
def checkout_from_cart(request):
    cart = get_or_create_cart(request)
    
    if cart.total_items == 0:
        messages.error(request, "Корзина пуста")
        return redirect('cart_view')
    
    # Проверяем наличие товаров на складе
    for item in cart.items.all():
        if item.quantity > item.product.stock:
            messages.error(request, 
                f"Товара '{item.product.name}' недостаточно на складе. "
                f"Доступно: {item.product.stock}, в корзине: {item.quantity}"
            )
            return redirect('cart_view')
    
    if request.method == 'POST':
        # Создаем заказ
        order = Order.objects.create(
            user=request.user,
            status='pending',
            total_amount=cart.total_price,
            delivery_address=request.POST.get('delivery_address', '')
        )
        
        # Переносим товары из корзины в заказ
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            
            # Уменьшаем остаток на складе
            item.product.stock -= item.quantity
            item.product.save()
        
        # Очищаем корзину
        cart.items.all().delete()
        
        messages.success(request, f"Заказ {order.order_number} успешно создан!")
        return redirect('order_detail', order_id=order.id)
    
    return render(request, 'accounts/checkout.html', {
        'cart': cart,
        'user': request.user
    })

# Декоратор для объединения корзин при входе
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

@receiver(user_logged_in)
def merge_carts_on_login(sender, request, user, **kwargs):
    """Объединить гостевую и пользовательскую корзины при входе"""
    session_cart = None
    if request.session.session_key:
        try:
            session_cart = Cart.objects.get(
                session_key=request.session.session_key,
                user=None
            )
        except Cart.DoesNotExist:
            pass
    
    user_cart = None
    try:
        user_cart = Cart.objects.get(user=user)
    except Cart.DoesNotExist:
        pass
    
    if session_cart:
        if user_cart:
            # Объединяем корзины
            merge_carts(session_cart, user_cart)
        else:
            # Присваиваем гостевую корзину пользователю
            session_cart.user = user
            session_cart.session_key = None
            session_cart.save()
    
    # Обновляем счетчик в сессии
    if user_cart:
        request.session['cart_count'] = user_cart.total_items
        # ======== ДОБАВЬТЕ ЭТИ ФУНКЦИИ В КОНЕЦ ФАЙЛА ========

def get_cart_count(request):
    """Возвращает количество товаров в корзине (для AJAX)"""
    from .cart_utils import get_or_create_cart
    cart = get_or_create_cart(request)
    count = sum(item.quantity for item in cart.items.all())
    return JsonResponse({'count': count})


def test_simple_add(request, product_id):
    """Тестовая страница для проверки добавления в корзину"""
    from django.http import HttpResponse
    from .models import Product, Cart, CartItem
    
    print(f"=== ТЕСТ: Добавление товара {product_id} ===")
    
    # Создаем сессию если нет
    if not request.session.session_key:
        request.session.create()
    
    # Создаем/получаем корзину
    cart, created = Cart.objects.get_or_create(
        session_key=request.session.session_key,
        user=None
    )
    print(f"Корзина ID: {cart.id}")
    
    # Находим товар
    try:
        product = Product.objects.get(id=product_id)
        print(f"Товар: {product.name}")
    except Product.DoesNotExist:
        return HttpResponse("<h1>Товар не найден</h1>")
    
    # Добавляем в корзину
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    # Обновляем счетчик
    total = sum(item.quantity for item in cart.items.all())
    request.session['cart_count'] = total
    
    print(f"✅ Добавлено! Всего в корзине: {total}")
    
    return HttpResponse(f"""
        <html>
        <head>
            <title>Товар добавлен</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 40px; }}
                .success {{ color: green; font-size: 24px; }}
                .info {{ background: #f8f9fa; padding: 20px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1 class="success">✅ Товар добавлен в корзину!</h1>
            
            <div class="info">
                <p><strong>Товар:</strong> {product.name}</p>
                <p><strong>Цена:</strong> {product.price} ₽</p>
                <p><strong>Корзина ID:</strong> {cart.id}</p>
                <p><strong>Товаров в корзине:</strong> {total}</p>
                <p><strong>Сессия:</strong> {request.session.session_key}</p>
            </div>
            
            <div style="margin-top: 30px;">
                <a href="/catalog/" style="padding: 10px 20px; background: #0d6efd; color: white; text-decoration: none; border-radius: 5px;">
                    ← Вернуться в каталог
                </a>
                <a href="/cart/" style="padding: 10px 20px; background: #198754; color: white; text-decoration: none; border-radius: 5px; margin-left: 10px;">
                    Перейти в корзину →
                </a>
            </div>
            
            <script>
                // Обновляем счетчик на всех открытых вкладках
                if (localStorage) {{
                    localStorage.setItem('cart_updated', Date.now());
                }}
            </script>
        </body>
        </html>
    """)