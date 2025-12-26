# wsgi.py для PythonAnywhere
import sys
import os

# Добавляем путь к проекту
path = '/home/dizalick05/rgz'  # ЗАМЕНИТЕ dizalick05 на ваш логин!
if path not in sys.path:
    sys.path.insert(0, path)
    sys.path.insert(0, os.path.join(path, 'backend'))

# Активируем виртуальное окружение если есть
activate_this = os.path.join(path, 'venv', 'bin', 'activate_this.py')
if os.path.exists(activate_this):
    with open(activate_this) as f:
        exec(f.read(), {'__file__': activate_this})

# Импортируем приложение
from backend.app import app as application

# Создаем базу данных если нужно
with application.app_context():
    from backend.models import db
    try:
        db.create_all()
        print(" База данных инициализирована")
    except Exception as e:
        print(f"⚠ Ошибка БД: {e}")