from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Category, Product, Order, OrderItem

# Настройка отображения CustomUser в админке
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'company_name', 'user_type', 'phone', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('user_type', 'phone', 'company_name', 'inn', 'address')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': ('user_type', 'phone', 'company_name', 'inn', 'address')
        }),
    )

# Позиции заказа внутри заказа (inline)
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ('total',)

# Настройка отображения заказов
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'user__username', 'user__company_name')
    inlines = [OrderItemInline]
    readonly_fields = ('order_number', 'created_at', 'updated_at')

# Настройка отображения товаров
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'price', 'stock', 'unit')
    list_filter = ('category',)
    search_fields = ('name', 'sku', 'description')

# Регистрация моделей в админке
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)