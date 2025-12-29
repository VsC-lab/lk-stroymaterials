#!/usr/bin/env python
"""
Полный скрипт для деплоя на Render
"""
import os
import sys
import django
import subprocess

def run_command(command, description):
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"STDERR: {result.stderr}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("🚀 Запуск полного деплоя на Render")
    
    # 1. Установка зависимостей
    if not run_command("pip install -r requirements.txt", "1. Установка зависимостей"):
        return
    
    # 2. Применение миграций
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lk_clone.settings')
    django.setup()
    
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'migrate', '--noinput'])
    
    # 3. Сборка статики
    execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
    
    # 4. Создание тестовых пользователей если их нет
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    test_users = [
        ('admin', 'admin12345', 'admin@example.com', True, True),
        ('testuser', 'test123', 'client@example.com', False, False),
        ('manager', 'manager12', 'manager@example.com', True, False),
    ]
    
    for username, password, email, is_staff, is_superuser in test_users:
        if not User.objects.filter(username=username).exists():
            User.objects.create_user(
                username=username,
                password=password,
                email=email,
                is_staff=is_staff,
                is_superuser=is_superuser
            )
            print(f"✅ Создан пользователь: {username}")
    
    print("\n🎉 Деплой завершен успешно!")

if __name__ == '__main__':
    main()