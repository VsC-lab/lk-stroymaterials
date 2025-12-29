import json
import sys

# Загрузите дамп
with open('db_backup.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Отфильтруйте данные
filtered_data = []
for item in data:
    # Исключаем системные таблицы которые создаются автоматически
    if item['model'] not in ['contenttypes.contenttype', 'sessions.session', 'admin.logentry']:
        filtered_data.append(item)

# Сохраните очищенный дамп
with open('db_filtered.json', 'w', encoding='utf-8') as f:
    json.dump(filtered_data, f, indent=2, ensure_ascii=False)

print(f"Очищено: {len(data) - len(filtered_data)} записей")
print(f"Сохранено: {len(filtered_data)} записей")