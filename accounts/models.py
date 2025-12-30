from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# 1. Кастомизированный пользователь
class CustomUser(AbstractUser):
    USER_TYPES = [
        ('client', 'Клиент'),
        ('partner', 'Партнер (поставщик)'),
        ('manager', 'Менеджер'),
    ]
    
    user_type = models.CharField('Тип пользователя', max_length=20, choices=USER_TYPES, default='client')
    phone = models.CharField('Телефон', max_length=20, blank=True)
    company_name = models.CharField('Название компании', max_length=200, blank=True)
    inn = models.CharField('ИНН', max_length=12, blank=True)
    address = models.TextField('Адрес', blank=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

# 2. Категория товаров
class Category(models.Model):
    name = models.CharField('Название категории', max_length=200)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Родительская категория')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

# 3. Товар
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    name = models.CharField('Название товара', max_length=300)
    sku = models.CharField('Артикул', max_length=100, unique=True)
    description = models.TextField('Описание', blank=True)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField('Остаток на складе', default=0)
    unit = models.CharField('Единица измерения', max_length=20, default='шт.')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    is_popular = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.name} ({self.sku})"
    
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

# 4. Заказ
class Order(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтвержден'),
        ('processing', 'В обработке'),
        ('shipped', 'Отгружен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Пользователь')
    order_number = models.CharField('Номер заказа', max_length=50, unique=True, editable=False)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='draft')
    total_amount = models.DecimalField('Общая сумма', max_digits=12, decimal_places=2, default=0)
    delivery_address = models.TextField('Адрес доставки', blank=True)
    comments = models.TextField('Комментарии', blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    
    def save(self, *args, **kwargs):
        """Сохранение заказа с генерацией номера"""
        if not self.order_number:
            from django.utils.timezone import now
            import random
            import time
            
            # Генерируем до 10 раз пока не найдем уникальный
            for attempt in range(10):
                try:
                    date_str = now().strftime('%y%m%d')
                    random_num = random.randint(1000, 9999)
                    proposed_number = f"ORD-{date_str}-{random_num:04d}"
                    
                    # Проверяем существование
                    if not Order.objects.filter(order_number=proposed_number).exists():
                        self.order_number = proposed_number
                        break
                        
                except Exception:
                    # Если ошибка, используем timestamp
                    pass
            
            # Если не удалось сгенерировать уникальный
            if not self.order_number:
                self.order_number = f"ORD-TS-{int(time.time())}-{random.randint(100, 999)}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Заказ {self.order_number} ({self.get_status_display()})"
    
class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

# 5. Позиция в заказе
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.PositiveIntegerField('Количество', default=1)
    price = models.DecimalField('Цена за единицу', max_digits=10, decimal_places=2)
    
    @property
    def total(self):
        return self.quantity * self.price
    
    def __str__(self):
        return f"{self.product.name} x{self.quantity}"
    
    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'
# 6. Корзина покупок
class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, 
                           verbose_name='Пользователь')
    session_key = models.CharField('Ключ сессии', max_length=40, null=True, blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    
    def __str__(self):
        if self.user:
            return f"Корзина пользователя {self.user.username}"
        else:
            return f"Корзина (сессия: {self.session_key})"
    
    @property
    def total_items(self):
        """Общее количество товаров в корзине"""
        from django.db.models import Sum  # ← ДОБАВЬТЕ ЭТУ СТРОКУ
        return self.items.aggregate(total=Sum('quantity'))['total'] or 0
    
    @property
    def total_price(self):
        """Общая стоимость корзины"""
        total = 0
        for item in self.items.all():
            total += item.quantity * item.product.price
        return total
    
    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

# 7. Позиция в корзине
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.PositiveIntegerField('Количество', default=1)
    added_at = models.DateTimeField('Дата добавления', auto_now_add=True)
    
    @property
    def price(self):
        """Цена товара"""
        return self.product.price
    
    @property
    def total(self):
        """Общая стоимость позиции"""
        return self.quantity * self.product.price
    
    def __str__(self):
        return f"{self.product.name} x{self.quantity}"
    
    class Meta:
        verbose_name = 'Позиция корзины'
        verbose_name_plural = 'Позиции корзины'
        unique_together = ['cart', 'product']  # Один товар - одна запись в корзине
# Create your models here.
