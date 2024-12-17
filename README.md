[![Main Foodgram Workflow](https://github.com/sunnnssses/foodgram/actions/workflows/main.yml/badge.svg)](https://github.com/sunnnssses/foodgram/actions/workflows/main.yml)

# Foodgram

## Описание проекта
Foodgram — это сервис, с помощью которого вы можете делиться рецептами, изучать новые и добавлять их в избранное, подписываться на авторов понравившихся рецептов и создавать список покупок по рецептам!

## Стек
- Python
- Django
- Django REST framework
- Djoser
- Nginx
- Docker
- Postgres

## Как развернуть проект
Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/sunnnssses/foodgram.git
cd foodgram
```
Выполнить запуск командой
```
sudo docker compose -f docker-compose.production.yml up -d
```
После запуска применить миграцию
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```
Выполнить сбор статики
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic

sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```
Загрузить список ингридиентов и тегов в базу данных
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py upload_ingredients "data/ingredients.json"

sudo docker compose -f docker-compose.production.yml exec backend python manage.py upload_tags "data/tags.json"
```
## Как развернуть проект локально
Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/sunnnssses/foodgram.git
cd foodgram
```
Применить миграции
```
cd backend/
python manage.py migrate
```
Загрузить список ингридиентов и тегов в базу данных
```
python manage.py upload_ingredients data/ingredients.json
python manage.py upload_tags data/tags.json
```
Запустить бэкенд
```
python manage.py runserver 8080
```
Запустить фронтенд
```
cd ../frontend/
npm i
npm run start
```

## Заполнение .env
Для работы проекта необходимо создать и заполнить файл .env следующими переменными окружения:
- ENGINE_DB='django.db.backends.postgresql_psycopg2'
- POSTGRES_DB=foodgram
- POSTGRES_USER=foodgram_user
- POSTGRES_PASSWORD=foodgram_password
- DB_HOST=db (либо DB_HOST=localhost)
- DB_PORT=5432
- SECRET_KEY='secret_key'
- ALLOWED_HOSTS='00.123.45.678,127.0.0.1,localhost'
- CSRF_TRUSTED_ORIGINS='https://*.ddns.net'
- DEBUG=False

##### Автор:  [Щеткина Елизавета](https://github.com/sunnnssses)