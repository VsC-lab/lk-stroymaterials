from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from accounts import views

urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/create/', views.create_order, name='create_order'),
    path('catalog/', views.product_catalog, name='catalog'),
    
    # Новые маршруты для корзины
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/', views.add_to_cart_view, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart_view, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item_view, name='update_cart_item'),
    path('cart/clear/', views.clear_cart_view, name='clear_cart'),
    path('cart/checkout/', views.checkout_from_cart, name='checkout_from_cart'),
    path('cart/get-count/', views.get_cart_count, name='get_cart_count'),
    path('test-simple-add/<int:product_id>/', views.test_simple_add, name='test_simple_add'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
]