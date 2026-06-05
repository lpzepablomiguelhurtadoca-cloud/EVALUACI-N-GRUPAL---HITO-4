from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from auth import login_required
from db import execute_query
from utils import log_auditoria

bp = Blueprint('productos', __name__, url_prefix='/productos')

@bp.route('/')
@login_required()
def listar():
    search = request.args.get('search', '')
    query = "SELECT * FROM productos WHERE 1=1"
    params = []
    if search:
        query += " AND (nombre_comercial LIKE %s OR codigo_unico LIKE %s)"
        params.extend([f'%{search}%', f'%{search}%'])
    query += " ORDER BY id DESC"
    productos = execute_query(query, params, fetch_all=True)
    return render_template('productos.html', productos=productos, search=search)

@bp.route('/guardar', methods=['POST'])
@login_required(rol='admin')
def guardar():
    data = request.form
    query = """
        INSERT INTO productos (codigo_unico, nombre_comercial, tipo, presentacion, graduacion_alcoholica, precio_actual, stock_minimo, stock_maximo)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = (data['codigo_unico'], data['nombre_comercial'], data['tipo_cerveza'], 
              data['presentacion'], data['graduacion'], data['precio'], 100, 10000)
    new_id = execute_query(query, params, commit=True)
    log_auditoria(session['username'], 'CREATE', 'productos', new_id, f'Creó producto {data["nombre_comercial"]}')
    flash('Producto registrado exitosamente.', 'success')
    return redirect(url_for('productos.listar'))

@bp.route('/editar/<int:id>')
@login_required(rol='admin')
def editar(id):
    producto = execute_query("SELECT * FROM productos WHERE id = %s", (id,), fetch_one=True)
    if not producto:
        flash('Producto no encontrado.', 'danger')
        return redirect(url_for('productos.listar'))
    return render_template('productos_editar.html', producto=producto)

@bp.route('/actualizar/<int:id>', methods=['POST'])
@login_required(rol='admin')
def actualizar(id):
    data = request.form
    query = """
        UPDATE productos SET codigo_unico=%s, nombre_comercial=%s, tipo=%s, presentacion=%s,
        graduacion_alcoholica=%s, precio_actual=%s, stock_minimo=%s, stock_maximo=%s
        WHERE id=%s
    """
    params = (data['codigo_unico'], data['nombre_comercial'], data['tipo_cerveza'],
              data['presentacion'], data['graduacion'], data['precio'], 100, 10000, id)
    execute_query(query, params, commit=True)
    log_auditoria(session['username'], 'UPDATE', 'productos', id, f'Actualizó producto ID {id}')
    flash('Producto actualizado.', 'success')
    return redirect(url_for('productos.listar'))

@bp.route('/eliminar/<int:id>')
@login_required(rol='admin')
def eliminar(id):
    # Verificar si el producto tiene lotes asociados
    lotes_asociados = execute_query("SELECT COUNT(*) as total FROM lotes WHERE producto_id = %s", (id,), fetch_one=True)
    if lotes_asociados['total'] > 0:
        flash('No se puede eliminar un producto que tiene lotes asociados.', 'danger')
        return redirect(url_for('productos.listar'))
    execute_query("DELETE FROM productos WHERE id = %s", (id,), commit=True)
    log_auditoria(session['username'], 'DELETE', 'productos', id, f'Eliminó producto ID {id}')
    flash('Producto eliminado.', 'success')
    return redirect(url_for('productos.listar'))