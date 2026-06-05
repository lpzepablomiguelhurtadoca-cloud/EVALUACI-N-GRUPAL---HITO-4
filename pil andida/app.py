from flask import Flask, render_template, request, redirect, url_for, flash, session
from config import Config
from auth import verificar_login, login_required
from utils import log_auditoria, obtener_metricas_dashboard
from db import execute_query

# Importar blueprints
from routes import (
    main,
    productos,
    lotes,
    inventario,
    distribuidores,
    reportes,
    admin,
    plantas_bodegas
)

app = Flask(__name__)
app.config.from_object(Config)

# Registrar blueprints
app.register_blueprint(main.bp)
app.register_blueprint(productos.bp)
app.register_blueprint(lotes.bp)
app.register_blueprint(inventario.bp)
app.register_blueprint(distribuidores.bp)
app.register_blueprint(reportes.bp)
app.register_blueprint(admin.bp)
app.register_blueprint(plantas_bodegas.bp)

# Ruta de login (se maneja en el blueprint main, pero la dejamos aquí para claridad)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = verificar_login(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['rol'] = user['rol']
            log_auditoria(username, 'LOGIN', detalles='Inicio de sesión exitoso')
            flash('Bienvenido al sistema.', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Usuario o contraseña incorrectos.', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    if 'username' in session:
        log_auditoria(session['username'], 'LOGOUT')
    session.clear()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('login'))

# Redirección desde raíz
@app.route('/')
def index():
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)