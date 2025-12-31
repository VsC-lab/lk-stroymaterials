## 🛠️ Технологический стек

### Бэкенд
- **Python 3.13** - основной язык
- **Django 6.0** - веб-фреймворк
- **PostgreSQL** - основная база данных
- **SQLite** - для локальной разработки

### Фронтенд
- **HTML5/CSS3** - семантическая верстка
- **JavaScript (ES6+)** - интерактивность
- **Bootstrap 5** - компоненты интерфейса
- **AJAX/Fetch API** - динамические обновления

### Инфраструктура и DevOps
- **Git/GitHub** - контроль версий
- **Render.com** - облачный хостинг
- **WhiteNoise** - статические файлы
- **Gunicorn** - WSGI сервер
- **dj-database-url** - конфигурация БД


### Структура проекта:
my_lk_project/
├── 📁 accounts/ # Основное приложение
│ ├── 📄 init.py
│ ├── 📄 admin.py # Регистрация моделей в админке
│ ├── 📄 apps.py # Конфигурация приложения
│ ├── 📄 models.py # Модели данных (500+ строк)
│ ├── 📄 views.py # Контроллеры (20+ views)
│ ├── 📄 urls.py # Маршруты приложения
│ ├── 📄 forms.py # Формы Django
│ ├── 📄 cart_utils.py # Логика работы с корзиной
│ ├── 📁 management/
│ │ └── 📁 commands/
│ │ ├── 📄 create_test_users.py
│ │ └── 📄 create_test_products.py
│ ├── 📁 migrations/ # Миграции базы данных
│ └── 📁 templates/ # HTML шаблоны
│ ├── 📁 accounts/
│ │ ├── 📄 base.html
│ │ ├── 📄 home.html
│ │ ├── 📄 login.html
│ │ ├── 📄 dashboard.html
│ │ ├── 📄 catalog.html
│ │ ├── 📄 cart.html
│ │ ├── 📄 checkout.html
│ │ ├── 📄 order_list.html
│ │ └── 📄 order_detail.html
│ └── 📁 includes/ # Частичные шаблоны
├── 📁 lk_clone/ # Настройки проекта Django
│ ├── 📄 init.py
│ ├── 📄 settings.py # Основная конфигурация
│ ├── 📄 urls.py # Корневые URL-адреса
│ ├── 📄 wsgi.py # WSGI конфигурация
│ └── 📄 asgi.py
├── 📁 static/ # Статические файлы
│ ├── 📁 css/
│ │ └── 📄 style.css
│ ├── 📁 js/
│ │ └── 📄 main.js
│ └── 📁 images/
├── 📁 media/ # Загружаемые пользователями файлы
├── 📄 .env # Переменные окружения (не в git)
├── 📄 .gitignore # Игнорируемые файлы
├── 📄 requirements.txt # Зависимости Python (15+ пакетов)
├── 📄 runtime.txt # Версия Python для Render
├── 📄 render.yaml # Конфигурация деплоя
├── 📄 README.md # Эта документация
├── 📄 LICENSE # Лицензия MIT
└── 📄 manage.py # Утилиты Django

### Конфигурация (render.yaml)
services:
  - type: web
    name: lk-stroymaterials
    runtime: python
    region: frankfurt
    plan: free
    buildCommand: |
      pip install -r requirements.txt
      python manage.py collectstatic --noinput
      python manage.py migrate
      python deploy_script.py
    startCommand: gunicorn lk_clone.wsgi:application
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: lkdb
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: "False"
      - key: DJANGO_ENV
        value: production
      - key: ALLOWED_HOSTS
        value: ".onrender.com"

databases:
  - name: lkdb
    plan: free
    databaseName: your-db-name
    user: lk_useryourdb_ctsh_user

## 📐 Архитектурные слои

### 🎨 **Презентационный слой (Frontend)**
- **HTML5/CSS3** - семантическая верстка
  - `accounts/templates/` - 15+ шаблонов
  - Bootstrap 5 - адаптивный дизайн
- **JavaScript** - интерактивность
  - AJAX/Fetch API - динамические обновления
  - DOM манипуляции - обновление интерфейса

### ⚙️ **Бизнес-логика (Backend)**
- **Контроллеры (Views)**
  - `accounts/views.py` - 20+ обработчиков запросов
  - Декораторы `@login_required`, `@require_POST`
  - Обработка форм и валидация
- **Модели (Models)**
  - `CustomUser` - расширенная модель пользователя
  - `Product`, `Category` - каталог товаров
  - `Order`, `OrderItem` - система заказов
  - `Cart`, `CartItem` - корзина покупок

### 🗄️ **Уровень данных (Data Layer)**
- **PostgreSQL** (продакшен)
  - Таблицы: 7 основных, 10+ связей
  - Индексы для оптимизации запросов
- **SQLite** (разработка)
  - Локальная БД для тестирования
- **Django ORM**
  - QuerySet API - построение запросов
  - Миграции - управление схемой БД
  - Сигналы - обработка событий

### 🌐 **Инфраструктура (Infrastructure)**
- **Хостинг**: Render.com (PaaS)
- **Сервер приложений**: Gunicorn
- **Статические файлы**: WhiteNoise + CDN
- **База данных**: Managed PostgreSQL


### Функциональность:
Каталог товаров (/catalog/)
Просмотр товаров по категориям

Фильтрация по наличию

Поиск по названию (в планах)

Пагинация

Корзина (/cart/)
Добавление/удаление товаров

Обновление количества (AJAX)

Расчет общей суммы

Очистка корзины

Оформление заказа (/cart/checkout/)
Форма с валидацией

Выбор способа доставки

Подтверждение заказа

Снижение остатков на складе

Личный кабинет (/dashboard/)
Статистика заказов

История покупок

Активные заказы

Общая сумма покупок
