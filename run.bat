@echo off

echo Activating virtual environment...
call .\env\Scripts\activate

echo Invoke...
py manage.py runserver

python manage.py runserver 0.0.0.0:8000

http://26.147.198.13:8000
