import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lk_clone.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import CustomUser

User = get_user_model()

def create_test_users():
    # Создаем администратора
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('admin12345')
        admin_user.save()
        print(f"✅ Создан администратор: admin / admin12345")
    else:
        print(f"ℹ️ Администратор уже существует")
    
    # Создаем клиента
    client_user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'client@example.com',
            'is_staff': False,
            'is_superuser': False
        }
    )
    if created:
        client_user.set_password('test123')
        client_user.save()
        print(f"✅ Создан клиент: testuser / test123")
    else:
        print(f"ℹ️ Клиент уже существует")
    
    # Создаем менеджера
    manager_user, created = User.objects.get_or_create(
        username='manager',
        defaults={
            'email': 'manager@example.com',
            'is_staff': True,
            'is_superuser': False
        }
    )
    if created:
        manager_user.set_password('manager12')
        manager_user.save()
        print(f"✅ Создан менеджер: manager / manager12")
    else:
        print(f"ℹ️ Менеджер уже существует")
    
    print("\n✅ Все тестовые пользователи созданы!")

if __name__ == '__main__':
    create_test_users()