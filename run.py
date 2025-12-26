import os
import sys
from flask import Flask, render_template, send_from_directory

# Добавляем backend в путь Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Импортируем основное приложение
from backend.app import app as backend_app

# Создаем основное приложение
app = Flask(__name__, 
            static_folder='frontend',
            template_folder='frontend')

# Подключаем все из backend
app.register_blueprint(backend_app)

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

# Статические файлы
@app.route('/<path:filename>')
def serve_static(filename):
    if filename.startswith('css/') or filename.startswith('js/'):
        return send_from_directory('frontend', filename)
    try:
        return send_from_directory('frontend', filename)
    except:
        return "Not found", 404

# Сохраняем секретный ключ
app.secret_key = 'banking-system-secret-key-2025'

if __name__ == '__main__':
    # Настраиваем базу данных
    with app.app_context():
        from backend.models import db
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///backend/database.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)
        db.create_all()
    
    app.run(debug=True, port=5000)