# Backend-приложение для автоматизации закупок (розничная сеть)

Данный проект реализует REST API для сервиса заказа товаров в розничной сети.  
Клиенты могут просматривать каталог, формировать корзину из товаров, оформлять заказы, получать подтверждение по e-mail.  
Поставщики могут обновлять свои прайс-листы, управлять приёмом заказов и просматривать поступившие заказы.
---

**Стек технологий:**
- Python 3.14+;
- Django 6.0.6, Django REST Framework 3.17;
- JWT-аутентификация (djangorestframework-simplejwt);
- Djoser (регистрация/управление пользователями);
- PostgreSQL 18 (база данных);
- Celery + Redis (асинхронная отправка e-mail);
- YAML (импорт товаров);
- Консольный e-mail-бэкенд.
                                                                                                               
**Среда разработки:**
- OS: Ubuntu 26.04 LTS «Resolute Raccoon»;
- IDE: PyCharm.

## Структура проекта
├── diplom/
- init.py
- celery.py 
- settings.py
- urls.py
- wsgi.py
  
├── users/ # Приложение «Пользователи».
- models.py 
- serializers.py
- views.py
- urls.py
- admin.py
  
├── products/ # Приложение «Товары и магазины».
- models.py
- serializers.py
- views.py
- urls.py
- admin.py
- management/commands/import_products.py # Импорт из YAML.
  
├── orders/ # Приложение «Корзина и заказы»
- models.py # Cart, CartItem, Order, OrderItem
- serializers.py
- views.py
- urls.py
- tasks.py # Celery-задачи для отправки e-mail.
- admin.py
  
├── shop.yaml # Пример файла импорта товаров.

├── requirements.txt

├── manage.py

└── .gitignore

## Модели данных

**Пользователь и контакты**
- **User** – кастомная модель, вход осуществляется по `email`, дополнительные поля: `first_name`, `last_name`, `middle_name`.
- **Contact** – контакты пользователя (адрес доставки / телефон).
Поля: `type` (choices: `phone` / `address`), `value` (строка с адресом или номером). </br>

**Товары и поставщики**
- **Shop** – магазин (поставщик): `name`, `url`, `is_active` (приём заказов).
- **Category** – категория товаров (`name`, связь M2M с `Shop`).
- **Product** – товар (`name`, `category`).
- **ProductInfo** – информация о товаре в конкретном магазине: `product`, `shop`, `external_id`, `name`, `quantity`, `price`, `price_rrc`.
- **Parameter** – название характеристики (например, «Диагональ»).
- **ProductParameter** – значение характеристики для конкретного `ProductInfo` (`product_info`, `parameter`, `value`).

**Корзина и заказы**
- **Cart** – корзина пользователя (связь 1:1 с `User`).
- **CartItem** – позиция корзины: `cart`, `product` (ссылка на `Product`), `quantity`, `shop`.
- **Order** – заказ: `user`, `status` (Новый/Подтверждён/В обработке/Доставлен/Отменён), `contact` (ссылка на `Contact`), `shipping_address` (адрес доставки).
- **OrderItem** – позиция заказа: `order`, `product` (ссылка на `Product`), `quantity`, `price`, `shop`.

### Установка и запуск (локально)
#### 1. Клонирование репозитория и создание виртуального окружения.
- git clone https://github.com/DeRini73/diploma/tree/main
- cd /diploma-main
- python3 -m venv .venv
- source .venv/bin/activate

#### 2. Установка зависимостей.
- pip install -r requirements.txt

#### 3. Создать в корне проекта файл .env следующего формата.
- DJANGO_SECRET_KEY=здесь будет ключ ваш
- DEBUG=True
- DB_NAME=имя вашей БД
- DB_USER=имя владельца БД
- DB_PASSWORD=пароль от БД
- DB_HOST=адрес хоста, например, localhost для локалки
- DB_PORT=адрес порта, например,5432

#### 4. Настройка базы данных PostgreSQL.
После установки и запуска PostgreSQL создайте пользователя и базу данных (учётные данные должны совпадать с настройками в settings.py).

Пример:
```
CREATE USER user WITH PASSWORD 'password';
CREATE DATABASE user_db OWNER user;
ALTER USER user CREATEDB;
```
*При возникновении ошибок с доступом к созданной базе данных рекомендую ознакомиться с материалом по ссылке: [Как исправить Connection Refused в PostgreSQL](https://app.incidenta.tech/library/error/databases/postgresql-connection-refused/)*

#### 5. Применение миграций и импорт товаров.
В терминале IDE применяем:
```
python manage.py makemigrations users products orders
python manage.py migrate
python manage.py import_products shop.yaml  # Импорт тестовых товаров.
```

#### 6. Создание суперпользователя и запуск сервера.
В терминале IDE создаем суперпользователя и следуем инструкциям:
```
python manage.py createsuperuser
```
Запуск сервера:
```
python manage.py runserver 0.0.0.0:8000
```
#### 7. Запуск Celery (для отправки e-mail).
Открываем дополнительный терминал в IDE  и применяем:
```
celery -A diplom worker -l info
```
E-mail будут выводиться в консоль Celery (настроен консольный бэкенд).

---

### API - документация
Базовый URL: http://127.0.0.1:8000/api/v1

### Аутентификация
**1. Регистрация пользователя.**
```
curl -X POST http://127.0.0.1:8000/api/v1/users/auth/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "mail@mail.com",
    "first_name": "Van",
    "last_name": "Vanich",
    "password": "122333"
  }'
```
Ответ (201 Created):
```
json
{
  "id": 1,
  "email": "mail@mail.com",
  "first_name": "Van",
  "last_name": "Vanich",
}
```
**2. Получение JWT-токена (авторизация).**
```
curl -X POST http://127.0.0.1:8000/api/v1/users/auth/jwt/create/ \
  -H "Content-Type: application/json" \
  -d '{"email":"mail@mail.com","password":"122333"}'
```
Ответ (200 OK):
```
json
{
  "refresh": "...",
  "access": "eyJhbGciOiJIUzI1NiIs..."
}
```
В качестве токена для последующих запросов используйте access токен в заголовке Authorization: Bearer.

**3. Контакты (адреса доставки).**
#### 3.1. Создание контакта
```
curl -X POST http://127.0.0.1:8000/api/v1/users/user/contacts/ \
  -H "Authorization: Bearer <токен>" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "address",
    "value": "г. Город, ул. Уличная, д. 10, кв. 25"
  }'
```
Ответ (201 Created):
```
json
{
  "id": 1,
  "type": "address",
  "value": "г. Город, ул. Уличная, д. 10, кв. 25"
}
```
#### 3.2. Список контактов
`GET /api/v1/users/user/contacts/`

#### 3.3. Удаление контакта
`DELETE /api/v1/users/user/contacts/{id}/`
####

**4. Товары.**
#### 4.1. Список всех доступных товаров.
`GET /api/v1/products/products/`

#### 4.2. Детали товара.
`GET /api/v1/products/products/{id}/`

Возвращает полную информацию о товаре.

**5. Корзина.**
#### 5.1. Просмотр корзины.
`GET /api/v1/orders/cart/`

#### 5.1. Добавление товара в корзину.
```
curl -X POST http://127.0.0.1:8000/api/v1/orders/cart/add_item/ \
  -H "Authorization: Bearer <токен>" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "quantity": 2
  }'
```
Ответ (201 Created): 
позиция корзины с полями id, product, product_name, quantity, shop, shop_name.

#### 5.2. Удаление позиции из корзины.
`POST /api/v1/orders/cart/remove_item/`

#### 5.3. Очистка корзины.
`POST /api/v1/orders/cart/clear/`
</br>

**6. Заказы.**
#### 6.1. Создание заказа (подтверждение).
Требуется указать contact_id контакта с типом address.
Товары берутся из корзины, далее, после создания заказа корзина очищается, а остатки уменьшаются на количество товаров из заказа.

```
curl -X POST http://127.0.0.1:8000/api/v1/orders/orders/ \
  -H "Authorization: Bearer <токен>" \
  -H "Content-Type: application/json" \
  -d '{"contact_id": 1}'
```
Ответ (201 Created): 
объект заказа с полями id, user, contact, contact_info, status, created_at, items, total_sum.

#### 6.1. Список заказов.
`GET /api/v1/orders/orders/` </br>

*Клиент видит только свои заказы, Администратор – все.*

#### 6.2. Детали заказа.
`GET /api/v1/orders/orders/{id}/`

#### 6.3. Изменение статуса заказа.
```
curl -X PATCH http://127.0.0.1:8000/api/v1/orders/orders/1/update_status/ \
  -H "Authorization: Bearer <токен>" \
  -H "Content-Type: application/json" \
  -d '{"status": "confirmed"}'
```
**7. Функции поставщика.**
#### 7.1. Обновление прайс-листа.
Принимает YAML-файл с данными товаров.
Обновляет категории, товары, характеристики и остатки.
```
curl -X POST http://127.0.0.1:8000/api/v1/supplier/update/ \
  -H "Authorization: Bearer <токен>" \
  -H "Content-Type: application/json" \
  -d '{"file": "shop: Связной\ncategories: ..."}'
```
#### 7.2. Включение/отключение приёма заказов.
```
curl -X POST http://127.0.0.1:8000/api/v1/supplier/status/ \
  -H "Authorization: Bearer <токен>" \
  -H "Content-Type: application/json" \
  -d '{"shop": "Связной", "is_active": false}'
```

---

## Полный сценарий работы
1. Регистрация: `POST /api/v1/users/auth/users/` </br>
2. Авторизация: `POST /api/v1/users/auth/jwt/create/` (для получения access токена). </br>
3. Добавление адреса доставки: `POST /api/v1/users/user/contacts/` (type=address). </br>
4. Просмотр каталога: `GET /api/v1/products/products/`. </br>
5. Добавление товаров в корзину: `POST /api/v1/orders/cart/add_item/`. </br>
6. Просмотр корзины: `GET /api/v1/orders/cart/`. </br>
7. Оформление заказа: `POST /api/v1/orders/orders/` с `contact_id`. </br>
8. Получение e-mail‑подтверждения: письма выводятся в консоль Celery. </br>
9. Просмотр заказов: `GET /api/v1/orders/orders/`, `GET /api/v1/orders/orders/{id}/`. </br>
10. Изменение статуса заказа (администратором): `PATCH/api/v1/orders/orders/{id}/update_status/`.
