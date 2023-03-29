# Foodgram
Сайт Foodgram, «Продуктовый помощник». На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.  
Проект доступен по адресу: http://158.160.46.55/
## Для запуска проекта:  
1. Клонировать репозиторий и перейти в него в командной строке:

```bash
  git clone https://github.com/Senkdar/foodgram-project-react/
  
  cd foodgram-project-react
```
2. Создать файл .env в папке infra с настройками:
 ```
SECRET_KEY=<КЛЮЧ>
DB_ENGINE=django.db.backends.postgresql
DB_NAME=<ИМЯ БАЗЫ ДАННЫХ>
POSTGRES_USER=<ИМЯ ПОЛЬЗОВАТЕЛЯ>
POSTGRES_PASSWORD=<ПАРОЛЬ>
DB_HOST=db
DB_PORT=5432
```
3. Выполнить команды:
```
docker-compose up -d
docker-compose exec backend python manage.py migrate  
docker-compose exec backend python manage.py collectstatic --noinput
```

4. Создать суперпользователя:
```
docker-compose exec backend python manage.py createsuperuser
```
### Админ зона
логин: admin  
пароль: admin  
email: admin@m.ru  

## API Reference

К проекту по адресу http://158.160.46.55/api/docs/redoc.html  
подключена документация API. В ней описаны возможные запросы к API и структура ожидаемых ответов.

