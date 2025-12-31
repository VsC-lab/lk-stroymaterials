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
* 📁 accounts/
** 📄 __init__.py
** 📄 admin.py
** 📄 apps.py
** 📄 models.py
*** CustomUser
*** Product
*** Category
*** Order
*** OrderItem
*** Cart
*** CartItem
** 📄 views.py
*** home()
*** login_view()
*** logout_view()
*** dashboard()
*** product_catalog()
*** cart_view()
*** add_to_cart_view()
*** remove_from_cart_view()
*** update_cart_item_view()
*** clear_cart_view()
*** checkout_from_cart()
*** order_list()
*** order_detail()
*** create_order()
*** get_cart_count()
*** test_simple_add()
** 📄 urls.py
** 📄 forms.py
** 📄 cart_utils.py
** 📁 management/
*** 📁 commands/
**** 📄 create_test_users.py
**** 📄 create_test_products.py
** 📁 migrations/
*** 📄 __init__.py
*** 📄 0001_initial.py
** 📁 templates/
*** 📁 accounts/
**** 📄 base.html
**** 📄 home.html
**** 📄 login.html
**** 📄 dashboard.html
**** 📄 catalog.html
**** 📄 cart.html
**** 📄 checkout.html
**** 📄 order_list.html
**** 📄 order_detail.html
**** 📄 create_order.html
*
* 📁 lk_clone/
** 📄 __init__.py
** 📄 settings.py
*** BASE_DIR
*** SECRET_KEY
*** DEBUG
*** DATABASES
*** INSTALLED_APPS
*** MIDDLEWARE
*** TEMPLATES
*** STATIC_URL/STATIC_ROOT
*** MEDIA_URL/MEDIA_ROOT
*** LOGIN_URL/LOGOUT_REDIRECT_URL
*** APP_CONFIG
** 📄 urls.py
** 📄 wsgi.py
** 📄 asgi.py
*
* 📁 static/
** 📁 css/
*** 📄 style.css
** 📁 js/
*** 📄 main.js
** 📁 images/
*** 📄 logo.png
*
* 📁 media/
** 📁 products/
** 📁 avatars/
*
* 📄 .env
* 📄 .gitignore
* 📄 requirements.txt
** Django>=5.0.2
** whitenoise==6.6.0
** dj-database-url==2.3.0
** gunicorn==21.2.0
** psycopg[binary]==3.1.18
** python-dotenv==1.0.0
* 📄 runtime.txt
* 📄 render.yaml
** services
** buildCommand
** startCommand
** envVars
* 📄 README.md
* 📄 LICENSE
* 📄 manage.py

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
