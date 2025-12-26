from functools import wraps
from flask import request, jsonify, session
from models import User

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print("=== login_required проверка ===")
        user_id = session.get('user_id')
        print(f"User ID из сессии: {user_id}")
        print(f"Сессия: {dict(session)}")
        
        if not user_id:
            print("ОШИБКА: Нет user_id в сессии")
            return jsonify({
                'jsonrpc': '2.0',
                'error': {'code': -32000, 'message': 'Требуется авторизация'},
                'id': request.json.get('id') if request.json else None
            }), 401
        
        user = User.query.get(user_id)
        if not user:
            print(f"ОШИБКА: Пользователь с ID {user_id} не найден")
            return jsonify({
                'jsonrpc': '2.0',
                'error': {'code': -32000, 'message': 'Пользователь не найден или заблокирован'},
                'id': request.json.get('id') if request.json else None
            }), 401
        
        if not user.is_active:
            print(f"ОШИБКА: Пользователь {user_id} не активен")
            return jsonify({
                'jsonrpc': '2.0',
                'error': {'code': -32000, 'message': 'Пользователь не найден или заблокирован'},
                'id': request.json.get('id') if request.json else None
            }), 401
        
        print(f"Успех: пользователь {user.login} авторизован")
        request.user = user
        return f(*args, **kwargs)
    return decorated_function
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'jsonrpc': '2.0',
                'error': {'code': -32000, 'message': 'Требуется авторизация'},
                'id': request.json.get('id') if request.json else None
            }), 401
        
        user = User.query.get(user_id)
        if not user or not user.is_active:
            return jsonify({
                'jsonrpc': '2.0',
                'error': {'code': -32000, 'message': 'Пользователь не найден или заблокирован'},
                'id': request.json.get('id') if request.json else None
            }), 401
        
        request.user = user
        return f(*args, **kwargs)
    return decorated_function

def manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(request, 'user'):
            return jsonify({
                'jsonrpc': '2.0',
                'error': {'code': -32000, 'message': 'Требуется авторизация'},
                'id': request.json.get('id') if request.json else None
            }), 401
        
        if request.user.role != 'manager':
            return jsonify({
                'jsonrpc': '2.0',
                'error': {'code': -32007, 'message': 'Доступ только для менеджеров'},
                'id': request.json.get('id') if request.json else None
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function

def client_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(request, 'user'):
            return jsonify({
                'jsonrpc': '2.0',
                'error': {'code': -32000, 'message': 'Требуется авторизация'},
                'id': request.json.get('id') if request.json else None
            }), 401
        
        if request.user.role != 'client':
            return jsonify({
                'jsonrpc': '2.0',
                'error': {'code': -32002, 'message': 'Только клиенты могут выполнять эту операцию'},
                'id': request.json.get('id') if request.json else None
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function