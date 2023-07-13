# Trello Pet Project

## Introduction

This is an imitation of a trello, with options for adding, using boards. It was made for purpose of practice with django and basic functions of django restframework. Thus used restframework views.APIView and serializers..Serializer.

## Technology
- Django, Django Restframework
- drf-yasg (Swagger)
- social auth for google authentication/registration
- Postgresql for database
- Docker, docker-compose

## Starting

### Setting up locally
First install environment and activate

```
python3 -m venv venv
source venv/bin/activate
```

Then install dependencies

> Before that it is recommended to upgrade pip

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```
Now you can run project
```
python manage.py runserver
```

### Setting up with docker

First you need to build docker

```
docker-compose build
```

Then you have to create migrations and super user

```
docker-compose run --rm web python manage.py makemigrations
docker-compose run --rm web python manage.py migrate
docker-compose run --rm web python manage.py createsuperuser
```
And now you can launch the project

```
docker-compose up
```
