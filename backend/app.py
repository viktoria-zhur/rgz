from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from models import db, User, Transaction
from validators import Validator
from auth import login_required, manager_required, client_required
import random
import os
import traceback

app = Flask(__name__)
app.config['SECRET_KEY'] = 'banking-system-secret-key-2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ВАЖНО: Добавляем домен, с которого работает фронтенд
CORS(app, 
     supports_credentials=True, 
     origins=['http://localhost:5000', 'http://127.0.0.1:5000'],
     allow_headers=['Content-Type'],
     methods=['GET', 'POST', 'OPTIONS'])

db.init_app(app)

# Добавляем обработку OPTIONS запросов для CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5000')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

def generate_account_number():
    return f"ACC{random.randint(1000, 9999)}"

def initialize_test_data():
    with app.app_context():
        if User.query.count() == 0:
            admin1 = User(
                login='admin1',
                full_name='Иванов Иван Иванович',
                role='manager',
                phone='+79991112233',
                account_number='ADMIN001'
            )
            admin1.set_password('admin123')
            db.session.add(admin1)
            
            admin2 = User(
                login='manager1',
                full_name='Петрова Анна Сергеевна',
                role='manager',
                phone='+79992223344',
                account_number='ADMIN002'
            )
            admin2.set_password('manager123')
            db.session.add(admin2)
            
            clients_data = [
                {'full_name': 'Сидоров Алексей Владимирович', 'phone': '+79161111111'},
                {'full_name': 'Кузнецова Мария Петровна', 'phone': '+79162222222'},
                {'full_name': 'Смирнов Дмитрий Алексеевич', 'phone': '+79163333333'},
                {'full_name': 'Васильева Екатерина Игоревна', 'phone': '+79164444444'},
                {'full_name': 'Попов Сергей Николаевич', 'phone': '+79165555555'},
                {'full_name': 'Новикова Ольга Викторовна', 'phone': '+79166666666'},
                {'full_name': 'Фёдоров Павел Александрович', 'phone': '+79167777777'},
                {'full_name': 'Морозова Анастасия Дмитриевна', 'phone': '+79168888888'},
                {'full_name': 'Волков Андрей Сергеевич', 'phone': '+79169999999'},
                {'full_name': 'Лебедева Татьяна Михайловна', 'phone': '+79160000000'}
            ]
            
            for i, client_data in enumerate(clients_data, 1):
                client = User(
                    login=f'client{i}',
                    full_name=client_data['full_name'],
                    role='client',
                    phone=client_data['phone'],
                    account_number=generate_account_number(),
                    balance=10000.00
                )
                client.set_password(f'client{i}')
                db.session.add(client)
            
            db.session.commit()
            print("Тестовые данные созданы")

# ==================== СТАТИЧЕСКИЕ ФАЙЛЫ ====================

@app.route('/')
def index():
    """Главная страница - фронтенд приложение"""
    try:
        return send_from_directory('../frontend', 'index.html')
    except Exception as e:
        print(f"Ошибка загрузки фронтенда: {e}")
        traceback.print_exc()
        return f"Ошибка загрузки фронтенда: {e}", 500

# Маршрут для CSS файлов
@app.route('/css/<path:filename>')
def serve_css(filename):
    try:
        return send_from_directory('../frontend/css', filename)
    except:
        return "CSS файл не найден", 404

# Маршрут для JS файлов
@app.route('/js/<path:filename>')
def serve_js(filename):
    try:
        return send_from_directory('../frontend/js', filename)
    except:
        return "JS файл не найден", 404

# ==================== API ====================

@app.route('/api', methods=['POST', 'OPTIONS'])
def jsonrpc_handler():
    # Обработка CORS preflight запросов
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    print("=" * 50)
    print("Получен API запрос")
    print(f"Метод: {request.method}")
    print(f"Заголовки: {dict(request.headers)}")
    print(f"Content-Type: {request.content_type}")
    
    try:
        # Проверяем, есть ли JSON данные
        if not request.is_json:
            print("ОШИБКА: Запрос не содержит JSON")
            print(f"Тело запроса: {request.data}")
            return jsonify({
                'jsonrpc': '2.0',
                'error': {'code': -32600, 'message': 'Invalid Request: Not JSON'},
                'id': None
            }), 400
        
        data = request.get_json()
        print(f"JSON данные: {data}")
        
        # Проверяем обязательные поля JSON-RPC
        if 'jsonrpc' not in data or data.get('jsonrpc') != '2.0':
            print("ОШИБКА: Неверная версия JSON-RPC")
            return jsonify({
                'jsonrpc': '2.0',
                'error': {'code': -32600, 'message': 'Invalid Request: Not JSON-RPC 2.0'},
                'id': None
            }), 400
        
        if 'method' not in data:
            print("ОШИБКА: Не указан метод")
            return jsonify({
                'jsonrpc': '2.0',
                'error': {'code': -32600, 'message': 'Invalid Request: No method specified'},
                'id': None
            }), 400
        
        method = data.get('method')
        params = data.get('params', {})
        request_id = data.get('id')
        
        print(f"Вызываем метод: {method}")
        print(f"Параметры: {params}")
        print(f"ID запроса: {request_id}")
        
        # Инициализируем тестовые данные
        initialize_test_data()
        
        handlers = {
            'login': handle_login,
            'logout': handle_logout,
            'verifyToken': handle_verify_token,
            'getAccountInfo': handle_get_account_info,
            'getTransactionHistory': handle_get_transaction_history,
            'transferMoney': handle_transfer_money,
            'getAllUsers': handle_get_all_users,
            'createUser': handle_create_user,
            'updateUser': handle_update_user,
            'deleteUser': handle_delete_user,
            'deleteAccount': handle_delete_account,
            'getStatistics': handle_get_statistics
        }
        
        if method in handlers:
            try:
                result = handlers[method](params)
                print(f"Метод {method} выполнен успешно")
                return jsonify({
                    'jsonrpc': '2.0',
                    'result': result,
                    'id': request_id
                })
            except Exception as e:
                print(f"ОШИБКА в методе {method}: {str(e)}")
                traceback.print_exc()
                return jsonify({
                    'jsonrpc': '2.0',
                    'error': {'code': -32000, 'message': str(e)},
                    'id': request_id
                }), 400
        else:
            print(f"ОШИБКА: Метод {method} не найден")
            return jsonify({
                'jsonrpc': '2.0',
                'error': {'code': -32601, 'message': f'Method {method} not found'},
                'id': request_id
            }), 404
            
    except Exception as e:
        print(f"ОШИБКА в jsonrpc_handler: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'jsonrpc': '2.0',
            'error': {'code': -32603, 'message': f'Internal error: {str(e)}'},
            'id': None
        }), 500

def handle_login(params):
    login = params.get('login')
    password = params.get('password')
    
    print(f"Логин: {login}, Пароль: {password}")
    
    is_valid, message = Validator.validate_login(login)
    if not is_valid:
        raise Exception(message)
    
    is_valid, message = Validator.validate_password(password)
    if not is_valid:
        raise Exception(message)
    
    user = User.query.filter_by(login=login).first()
    if not user:
        print(f"Пользователь с логином {login} не найден")
        raise Exception('Неверный логин или пароль')
    
    if not user.check_password(password):
        print(f"Неверный пароль для пользователя {login}")
        raise Exception('Неверный логин или пароль')
    
    if not user.is_active:
        print(f"Пользователь {login} не активен")
        raise Exception('Пользователь заблокирован')
    
    session['user_id'] = user.id
    print(f"Успешная авторизация для пользователя {user.id}")
    
    return {
        'user': user.to_dict()
    }

def handle_logout(params):
    session.clear()
    return {'success': True}

def handle_verify_token(params):
    user_id = session.get('user_id')
    if not user_id:
        raise Exception('Не авторизован')
    
    user = User.query.get(user_id)
    if not user or not user.is_active:
        raise Exception('Пользователь не найден')
    
    return {'valid': True}

@login_required
def handle_get_account_info(params):
    return request.user.to_dict()

@login_required
@client_required
def handle_get_transaction_history(params):
    transactions = Transaction.query.filter(
        (Transaction.sender_id == request.user.id) | 
        (Transaction.receiver_id == request.user.id)
    ).order_by(Transaction.created_at.desc()).all()
    
    result = []
    for tx in transactions:
        tx_dict = tx.to_dict()
        if tx.sender_id == request.user.id:
            tx_dict['type'] = 'outgoing'
            tx_dict['counterparty'] = tx.receiver.full_name
        else:
            tx_dict['type'] = 'incoming'
            tx_dict['counterparty'] = tx.sender.full_name
        result.append(tx_dict)
    
    return result

@login_required
@client_required
def handle_transfer_money(params):
    recipient = params.get('recipient')
    amount = params.get('amount')
    
    is_valid, message = Validator.validate_amount(amount)
    if not is_valid:
        raise Exception(message)
    
    amount = float(amount)
    
    if request.user.balance < amount:
        raise Exception('Недостаточно средств')
    
    receiver = User.query.filter(
        (User.account_number == recipient) | (User.phone == recipient)
    ).first()
    
    if not receiver or receiver.role != 'client':
        raise Exception('Получатель не найден')
    
    if receiver.id == request.user.id:
        raise Exception('Нельзя переводить самому себе')
    
    request.user.balance -= amount
    receiver.balance += amount
    
    transaction = Transaction(
        sender_id=request.user.id,
        receiver_id=receiver.id,
        amount=amount,
        description=f'Перевод {recipient}'
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    return {
        'success': True,
        'transaction_id': transaction.id,
        'new_balance': round(request.user.balance, 2)
    }

@login_required
@manager_required
def handle_get_all_users(params):
    users = User.query.filter_by(is_active=True).all()
    return [user.to_dict() for user in users]

@login_required
@manager_required
def handle_create_user(params):
    login = params.get('login')
    password = params.get('password')
    full_name = params.get('fullName')
    role = params.get('role', 'client')
    phone = params.get('phone')
    account_number = params.get('accountNumber')
    balance = params.get('balance', 1000.0 if role == 'client' else 0)
    
    for field, value, validator in [
        ('login', login, Validator.validate_login),
        ('password', password, Validator.validate_password),
        ('full_name', full_name, Validator.validate_full_name),
        ('phone', phone, Validator.validate_phone),
        ('account_number', account_number, Validator.validate_account_number),
        ('balance', balance, Validator.validate_balance)
    ]:
        is_valid, message = validator(value)
        if not is_valid:
            raise Exception(f'{field}: {message}')
    
    if User.query.filter_by(login=login).first():
        raise Exception('Логин уже существует')
    
    if role == 'client':
        if not account_number:
            account_number = generate_account_number()
        if User.query.filter_by(account_number=account_number).first():
            raise Exception('Номер счета уже существует')
    
    user = User(
        login=login,
        full_name=full_name,
        role=role,
        phone=phone,
        account_number=account_number if role == 'client' else None,
        balance=float(balance)
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    return user.to_dict()

@login_required
@manager_required
def handle_update_user(params):
    user_id = params.get('id')
    updates = {k: v for k, v in params.items() if k != 'id'}
    
    user = User.query.get(user_id)
    if not user:
        raise Exception('Пользователь не найден')
    
    if 'login' in updates:
        is_valid, message = Validator.validate_login(updates['login'])
        if not is_valid:
            raise Exception(message)
        if User.query.filter(User.login == updates['login'], User.id != user_id).first():
            raise Exception('Логин уже существует')
    
    if 'password' in updates:
        is_valid, message = Validator.validate_password(updates['password'])
        if not is_valid:
            raise Exception(message)
        user.set_password(updates['password'])
        del updates['password']
    
    if 'full_name' in updates:
        is_valid, message = Validator.validate_full_name(updates['full_name'])
        if not is_valid:
            raise Exception(message)
    
    if 'phone' in updates:
        is_valid, message = Validator.validate_phone(updates['phone'])
        if not is_valid:
            raise Exception(message)
    
    if 'balance' in updates:
        is_valid, message = Validator.validate_balance(updates['balance'])
        if not is_valid:
            raise Exception(message)
    
    for key, value in updates.items():
        if hasattr(user, key):
            setattr(user, key, value)
    
    db.session.commit()
    return user.to_dict()

@login_required
@manager_required
def handle_delete_user(params):
    user_id = params.get('id')
    
    if user_id == request.user.id:
        raise Exception('Нельзя удалить самого себя')
    
    user = User.query.get(user_id)
    if not user:
        raise Exception('Пользователь не найден')
    
    user.is_active = False
    db.session.commit()
    
    return {'success': True}

@login_required
def handle_delete_account(params):
    request.user.is_active = False
    db.session.commit()
    session.clear()
    return {'success': True}

@login_required
@manager_required
def handle_get_statistics(params):
    users = User.query.filter_by(is_active=True).all()
    total_users = len(users)
    total_managers = len([u for u in users if u.role == 'manager'])
    total_clients = len([u for u in users if u.role == 'client'])
    total_balance = sum([u.balance for u in users if u.role == 'client'])
    
    return {
        'total_users': total_users,
        'total_managers': total_managers,
        'total_clients': total_clients,
        'total_balance': round(total_balance, 2)
    }

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("База данных инициализирована")
    
    print("=" * 60)
    print("БАНКОВСКАЯ СИСТЕМА ЗАПУЩЕНА!")
    print("=" * 60)
    print("Сервер доступен по адресу: http://localhost:5000")
    print("\nДемо доступы:")
    print("-" * 40)
    print("Менеджеры:")
    print("  Логин: admin1     Пароль: admin123")
    print("  Логин: manager1   Пароль: manager123")
    print("\nКлиенты:")
    print("  Логин: client1    Пароль: client1")
    print("  Логин: client2    Пароль: client2")
    print("  ... и так до client10")
    print("=" * 60)
    
    app.run(debug=True, port=5000, host='0.0.0.0')