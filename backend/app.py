from flask import Flask, request, jsonify, session
from flask_cors import CORS
from models import db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'banking-system-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app, supports_credentials=True, origins=['http://localhost:3000'])
db.init_app(app)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Банковская система</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            .student-info { background: #f0f0f0; padding: 15px; margin: 20px 0; border-left: 4px solid #3498db; }
        </style>
    </head>
    <body>
        <h1>Банковская система - API</h1>
        <div class="student-info">
            <strong>Студент:</strong> Виктория Журавлева<br>
            <strong>Группа:</strong> ФБИ-34, 2025 год
        </div>
        <p>API доступно по адресу: /api</p>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True, port=5000)