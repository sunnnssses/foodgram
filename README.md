# Foodgram

## Описание проекта
Foodgram — это сервис, с помощью которого вы можете делиться рецептами, изучать новые и добавлять их в избранное, подписываться на авторов понравившихся рецептов и создавать список покупок по рецептам!

## Стек
- Python 3.9
- Django 3.2.16
- Nginx
- Docker
- Postgres

## Как развернуть проект
Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/sunnnssses/foodgram.git
```
```
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
## Заполнение .env
Для работы проекта необходимо создать и заполнить файл .env следующими переменными окружения:
- POSTGRES_DB=foodgram
- POSTGRES_USER=foodgram_user
- POSTGRES_PASSWORD=foodgram_password
- DB_HOST=db
- DB_PORT=5432
- SECRET_KEY = 'secret_key'
- ALLOWED_HOSTS = '00.123.45.678'
- DEBUG = False

##### Автор: sunnnssses
