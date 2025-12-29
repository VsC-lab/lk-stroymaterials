import os
import django
import json
import sys

# Настройки для Render
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lk_clone.settings')
django.setup()

from django.core.management import call_command
from django.db import transaction

def load_data():
    print("🔄 Загрузка данных в базу данных Render...")
    
    # Применяем миграции
    print("1. Применяем миграции...")
    call_command('migrate', '--noinput')
    
    # Очищаем старые данные (опционально)
    print("2. Очистка старых данных...")
    # Можно добавить очистку конкретных таблиц если нужно
    
    # Загружаем данные
    print("3. Загрузка данных из дампа...")
    try:
        with open('db_filtered.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Загружаем частями чтобы избежать ошибок
        chunk_size = 100
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i + chunk_size]
            temp_file = f'temp_chunk_{i}.json'
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(chunk, f, ensure_ascii=False)
            
            call_command('loaddata', temp_file)
            os.remove(temp_file)
            
            print(f"   Загружено {min(i + chunk_size, len(data))}/{len(data)} записей")
        
        print("✅ Данные успешно загружены!")
        
    except Exception as e:
        print(f"❌ Ошибка при загрузке данных: {e}")
        sys.exit(1)

if __name__ == '__main__':
    load_data()