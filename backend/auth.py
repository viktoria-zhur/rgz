from functools import wraps
from flask import request, jsonify, session
from models import User

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