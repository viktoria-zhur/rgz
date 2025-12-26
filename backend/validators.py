import re

class Validator:
    @staticmethod
    def validate_login(login):
        if not login or len(login) < 3:
            return False, "Логин должен содержать минимум 3 символа"
        if len(login) > 50:
            return False, "Логин слишком длинный (максимум 50 символов)"
        if not re.match(r'^[a-zA-Z0-9_.-]+$', login):
            return False, "Логин может содержать только латинские буквы, цифры, точку, дефис и подчеркивание"
        return True, ""
    
    @staticmethod
    def validate_password(password):
        if not password or len(password) < 6:
            return False, "Пароль должен содержать минимум 6 символов"
        if len(password) > 100:
            return False, "Пароль слишком длинный"
        if not re.match(r'^[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]+$', password):
            return False, "Пароль содержит недопустимые символы"
        return True, ""
    
    @staticmethod
    def validate_full_name(full_name):
        if not full_name or len(full_name.strip()) < 2:
            return False, "ФИО обязательно для заполнения"
        if len(full_name) > 100:
            return False, "ФИО слишком длинное"
        return True, ""
    
    @staticmethod
    def validate_phone(phone):
        if phone:
            if not re.match(r'^\+?[1-9]\d{9,14}$', phone):
                return False, "Некорректный формат телефона"
        return True, ""
    
    @staticmethod
    def validate_account_number(account_number):
        if account_number:
            if not re.match(r'^ACC\d{4,10}$', account_number):
                return False, "Номер счета должен начинаться с ACC и содержать цифры"
        return True, ""
    
    @staticmethod
    def validate_amount(amount):
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                return False, "Сумма должна быть положительной"
            if amount_float > 1000000:
                return False, "Сумма не может превышать 1,000,000"
            return True, ""
        except (ValueError, TypeError):
            return False, "Некорректная сумма"
    
    @staticmethod
    def validate_balance(balance):
        try:
            balance_float = float(balance)
            if balance_float < 0:
                return False, "Баланс не может быть отрицательным"
            return True, ""
        except (ValueError, TypeError):
            return False, "Некорректный баланс"