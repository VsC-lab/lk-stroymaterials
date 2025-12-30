from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Sum, Count
from django.http import JsonResponse
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.http import require_POST, require_http_methods

from .models import Order, Product, OrderItem, Cart, CartItem, CustomUser
from .forms import OrderForm, OrderItemFormSet, CartItemForm, UserRegistrationForm
from .cart_utils import (
    get_or_create_cart, add_to_cart, remove_from_cart, 
    update_cart_item, get_cart_items_count, clear_cart, merge_carts
)

# ==================== АУТЕНТИФИКАЦИЯ ====================

def login_view(request):
    """Страница входа в систему"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f"Добро пожаловать, {user.username}!")
                
                # Перенаправляем на страницу, с которой пришли, или на главную
                next_page = request.GET.get('next', 'home')
                return redirect(next_page)
            else:
                messages.error(request, "Неверное имя пользователя или пароль")
        else:
            messages.error(request, "Ошибка в форме входа")
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

@require_POST
def logout_view(request):
    """Выход из системы"""
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "Вы успешно вышли из системы")
    return redirect('home')

def register_view(request):
    """Регистрация нового пользователя"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Автоматически входим после регистрации
            login(request, user)
            
            messages.success(request, f"Регистрация успешна! Добро пожаловать, {user.username}!")
            return redirect('home')
        else:
            messages.error(request, "Исправьте ошибки в форме")
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

# ==================== ГЛАВНАЯ СТРАНИЦА ====================
def home(request):
    """Главная страница"""
    try:
        # Все товары в наличии
        available_products = Product.objects.filter(stock__gt=0)
        
        # 1. Популярные товары
        popular_products = available_products.filter(is_popular=True)[:8]
        
        # Если популярных мало (меньше 4), добавляем другие
        if popular_products.count() < 4:
            additional = available_products.exclude(
                id__in=[p.id for p in popular_products]
            )[:8 - popular_products.count()]
            popular_products = list(popular_products) + list(additional)
        
        # 2. Новинки
        new_products = available_products.order_by('-created_at')[:8]
        
    except Exception as e:
        print(f"Error in home view: {e}")
        
        # В случае ошибки показываем все товары
        popular_products = Product.objects.all()[:8]
        new_products = Product.objects.order_by('-created_at')[:8]
    
    # Статистика
    total_products = Product.objects.count()
    in_stock_count = Product.objects.filter(stock__gt=0).count()
    
    context = {
        'popular_products': popular_products,
        'new_products': new_products,
        'total_products': total_products,
        'in_stock_count': in_stock_count,
        'user': request.user
    }
    
    return render(request, 'accounts/home.html', context)

# ==================== ЛИЧНЫЙ КАБИНЕТ ====================

@login_required
def dashboard(request):
    """Личный кабинет пользователя"""
    user_orders = Order.objects.filter(user=request.user)
    
    stats = {
        'total_orders': user_orders.count(),
        'total_spent': user_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
        'active_orders': user_orders.exclude(status__in=['delivered', 'cancelled']).count(),
    }
    
    recent_orders = user_orders.order_by('-created_at')[:5]
    
    return render(request, 'accounts/dashboard.html', {
        'stats': stats,
        'recent_orders': recent_orders,
    })

# ==================== ЗАКАЗЫ ====================

@login_required
def order_list(request):
    """Список заказов пользователя"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/order_list.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    """Детали заказа"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'accounts/order_detail.html', {'order': order})

@login_required
def create_order(request):
    """Создание нового заказа"""
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

# ==================== КАТАЛОГ ====================

def product_catalog(request):
    """Каталог товаров"""
    products = Product.objects.filter(stock__gt=0)
    categories = {}
    
    for product in products:
        if product.category not in categories:
            categories[product.category] = []
        categories[product.category].append(product)
    
    return render(request, 'accounts/catalog.html', {'categories': categories})

# ==================== КОРЗИНА ====================

def cart_view(request):
    """Просмотр корзины"""
    cart = get_or_create_cart(request)
    items = cart.items.all().select_related('product')
    
    # Формы для изменения количества
    item_forms = {}
    for item in items:
        item_forms[item.id] = CartItemForm(instance=item)
    
    total_price = sum(item.product.price * item.quantity for item in items)
    
    return render(request, 'accounts/cart.html', {
        'cart': cart,
        'items': items,
        'item_forms': item_forms,
        'total_price': total_price,
    })

def add_to_cart_view(request, product_id):
    """Добавить товар в корзину"""
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
            success, message = add_to_cart(request, product_id, quantity)
            
            # Для AJAX запросов
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
                return redirect(request.META.get('HTTP_REFERER', 'catalog'))
                
        except ValueError:
            messages.error(request, "Неверное количество")
            return redirect('catalog')
    
    return redirect('catalog')

@require_POST
def remove_from_cart_view(request, item_id):
    """Удалить товар из корзины"""
    success, message = remove_from_cart(request, item_id)
    
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
        return redirect('cart_view')

@require_POST
def update_cart_item_view(request, item_id):
    """Обновить количество товара в корзине"""
    try:
        quantity = int(request.POST.get('quantity', 1))
        success, message = update_cart_item(request, item_id, quantity)
        
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
    except ValueError:
        messages.error(request, "Неверное количество")
    
    return redirect('cart_view')

@require_POST
def clear_cart_view(request):
    """Очистить корзину"""
    success, message = clear_cart(request)
    
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    
    return redirect('cart_view')

# ==================== ОФОРМЛЕНИЕ ЗАКАЗА ====================

@login_required
@require_http_methods(["GET", "POST"])
def checkout_from_cart(request):
    """Оформить заказ из корзины"""
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
            delivery_address=request.POST.get('delivery_address', ''),
            phone=request.POST.get('phone', ''),
            email=request.POST.get('email', request.user.email)
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
    })

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================

def get_cart_count(request):
    """Возвращает количество товаров в корзине (для AJAX)"""
    cart = get_or_create_cart(request)
    count = sum(item.quantity for item in cart.items.all())
    return JsonResponse({'count': count})

def test_simple_add(request, product_id):
    """Тестовая страница для проверки добавления в корзину"""
    if not request.session.session_key:
        request.session.create()
    
    cart, created = Cart.objects.get_or_create(
        session_key=request.session.session_key,
        user=None
    )
    
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Товар не найден'})
    
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
    
    return JsonResponse({
        'success': True,
        'message': f'Товар {product.name} добавлен в корзину',
        'cart_count': total
    })