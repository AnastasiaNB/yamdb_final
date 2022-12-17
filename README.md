# yamdb_final       
yamdb_final   
![](https://github.com/AnastasiaNB/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)
Cтек технологий:
Python Django Django REST Framework PostgreSQL JWT Nginx gunicorn Docker Docker-compose DockerHub GitHubActions Yandex.Cloud

Запуск проекта:
Клонировать репозиторий и перейти в него в командной строке:         

```git clone git@github.com:AnastasiaNB/yamdb_final.git```
```cd api_yamdb/```

Cоздать и активировать виртуальное окружение:

```python3 -m venv venv``` 
```source venv/bin/activate``` 
```python3 -m pip install --upgrade pip```

Установить зависимости из файла requirements.txt:

```pip install -r requirements.txt```

Запустить приложение в контейнерах:

из директории infra/

```docker-compose up -d --build```

Выполнить миграции:

из директории infra/

```docker-compose exec web python manage.py migrate```

Создать суперпользователя:

из директории infra/

```docker-compose exec web python manage.py createsuperuser```

Собрать статику:

из директории infra/

```docker-compose exec web python manage.py collectstatic --no-input```

Остановить приложение в контейнерах:

из директории infra/

```docker-compose down -v```
