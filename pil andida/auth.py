from flask import session, redirect, url_for, flash
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from db import execute_query

def crear_usuario(username, password, rol, nombre_completo=None):
    hashed = generate_password_hash(password)
    query = """
        INSERT INTO usuarios_sistema (username, password_hash, rol, nombre_completo, activo)
        VALUES (%s, %s, %s, %s, 1)
    """
    return execute_query(query, (username, hashed, rol, nombre_completo), commit=True)

def verificar_login(username, password):
    query = "SELECT id, username, rol, activo, password_hash FROM usuarios_sistema WHERE username = %s"
    user = execute_query(query, (username,), fetch_one=True)
    if user and user['activo'] == 1 and check_password_hash(user['password_hash'], password):
        return user
    return None

def login_required(rol=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Debe iniciar sesión.', 'warning')
                return redirect(url_for('login'))
            if rol and session.get('rol') != rol and session.get('rol') != 'admin':
                flash('No tiene permisos para acceder a esta sección.', 'danger')
                # CORRECCIÓN: redirigir al dashboard del blueprint 'main'
                return redirect(url_for('main.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator