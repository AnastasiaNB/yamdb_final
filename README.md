# yamdb_final          
![](https://github.com/AnastasiaNB/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)
#### Cтек технологий:
Python Django Django REST Framework PostgreSQL JWT Nginx gunicorn Docker Docker-compose DockerHub GitHubActions Yandex.Cloud

### Запуск проекта:
#### В репозитории на Гитхабе добавьте данные в Settings - Secrets - Actions secrets:
* ```DOCKER_USERNAME - имя пользователя в DockerHub```
* ```DOCKER_PASSWORD - пароль пользователя в DockerHub```
* ```HOST - ip-адрес сервера```
* ```USER - пользователь```
* ```SSH_KEY - приватный ssh-ключ (публичный должен быть на сервере)```
* ```PASSPHRASE - кодовая фраза для ssh-ключа```
* ```DB_ENGINE - django.db.backends.postgresql```
* ```DB_HOST - db```
* ```DB_PORT - 5432```
* ```ALLOWED_HOSTS - список разрешённых адресов```
* ```TELEGRAM_TO - id своего телеграм-аккаунта (можно узнать у @userinfobot, команда /start)```
* ```TELEGRAM_TOKEN - токен бота (получить токен можно у @BotFather, /token, имя бота)```
* ```DB_NAME - postgres (по умолчанию)```
* ```POSTGRES_USER - postgres (по умолчанию)```
* ```POSTGRES_PASSWORD - postgres (по умолчанию)```
#### Установите Docker и Docker-compose:
* ```sudo apt install docker.io```
* ```sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o usr/local/bin/docker-compose```
* ```sudo chmod +x /usr/local/bin/docker-compose```
#### Выполнить команды для сбора статики;
* ```sudo docker-compose exec web python manage.py collectstatic --no-input```
#### создания и применения миграций;
* ```sudo docker-compose exec web python manage.py makemigrations```
* ```sudo docker-compose exec web python manage.py migrate --noinput```
#### создания суперпользователя.
* ```sudo docker-compose exec web python manage.py createsuperuser```

#### Для проверки: 
ip сервера - 158.160.33.81