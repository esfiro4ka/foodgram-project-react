# praktikum_new_diplom

![workflow](https://github.com/esfiro4ka/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

## Развернутый проект

http://51.250.78.56/

## Описание
Cайт Foodgram, «Продуктовый помощник» - это онлайн-сервис и API для него. На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Запуск проекта с помощью Docker

- Установить Docker, используя инструкции с официального сайта:

https://www.docker.com/

- Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:esfiro4ka/foodgram-project-react.git

cd foodgram-project-react

```

- Перейти в директорию infra и создать файл .env:

```
cd infra

touch .env
```

- Добавить в файл .env переменные окружения для работы с базой данных:

```
SECRET_KEY='%0wetsg%6#w3bn!$1i+1xl%ind%*1m5k-j24g@8lh((^-+u@w_'
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД 
```

- Запустить docker-compose:

```
docker-compose up -d
```

- Выполнить миграции:

```
docker-compose exec backend python manage.py migrate
```

- Создать суперпользователя:

```
docker-compose exec backend python manage.py createsuperuser
```

- Собрать статику:

```
docker-compose exec backend python manage.py collectstatic --no-input
```

- Заполнить данными базы данных Теги и Ингредиенты:

```
docker-compose exec backend python manage.py load_csv
```

## Примеры запросов

- Админка

```
http://localhost:80/admin/
```

- Документация к проекту

```
http://localhost:80/api/docs/redoc/
```

## Стек технологий

Python 3.7, Django 3.2.19, Django REST Framework 3.14.0, PostgreSQL 13.0, Djoser 2.1.0.

## Авторы

Ротбардт Ольга.
