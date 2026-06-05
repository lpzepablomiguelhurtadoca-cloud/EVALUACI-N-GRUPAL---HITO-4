from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from auth import login_required
from db import execute_query
from utils import log_auditoria

bp = Blueprint('distribuidores', __name__, url_prefix='/distribuidores')

@bp.route('/')
@login_required()
def index():
    distribuidores = execute_query("SELECT * FROM distribuidores ORDER BY razon_social", fetch_all=True)
    pedidos = execute_query("""
        SELECT p.*, d.razon_social as distribuidor_nombre
        FROM pedidos p
        JOIN distribuidores d ON p.distribuidor_id = d.id
        ORDER BY p.fecha_pedido DESC
    """, fetch_all=True)
    productos = execute_query("SELECT id, nombre_comercial, presentacion FROM productos ORDER BY nombre_comercial", fetch_all=True)
    return render_template('distribuidores.html', distribuidores=distribuidores, pedidos=pedidos, productos=productos)

@bp.route('/crear', methods=['POST'])
@login_required()
def crear_pedido():
    distribuidor_id = request.form.get('distribuidor_id')
    fecha_entrega = request.form.get('fecha_entrega')
    producto_id = request.form.get('item_producto')
    cantidad = int(request.form.get('item_cantidad', 0))
    
    if not distribuidor_id or not fecha_entrega or not producto_id or cantidad <= 0:
        flash('Faltan datos obligatorios.', 'danger')
        return redirect(url_for('distribuidores.index'))
    
    # Obtener precio del producto
    producto = execute_query("SELECT precio_actual FROM productos WHERE id = %s", (producto_id,), fetch_one=True)
    if not producto:
        flash('Producto no encontrado.', 'danger')
        return redirect(url_for('distribuidores.index'))
    
    monto_total = cantidad * producto['precio_actual']
    
    # Insertar pedido
    query_pedido = """
        INSERT INTO pedidos (distribuidor_id, fecha_pedido, fecha_entrega_requerida, estado, monto_total, estado_pago)
        VALUES (%s, CURDATE(), %s, 'Pendiente', %s, 'Pendiente')
    """
    pedido_id = execute_query(query_pedido, (distribuidor_id, fecha_entrega, monto_total), commit=True)
    
    # Insertar detalle
    query_detalle = """
        INSERT INTO pedidos_detalle (pedido_id, producto_id, cantidad, precio_unitario)
        VALUES (%s, %s, %s, %s)
    """
    execute_query(query_detalle, (pedido_id, producto_id, cantidad, producto['precio_actual']), commit=True)
    
    log_auditoria(session['username'], 'CREATE', 'pedidos', pedido_id, f'Pedido creado para distribuidor {distribuidor_id}')
    flash('Pedido registrado exitosamente.', 'success')
    return redirect(url_for('distribuidores.index'))

@bp.route('/despachar/<int:id>', methods=['POST'])
@login_required()
def despachar_pedido(id):
    # Cambiar estado a 'Despachado'
    execute_query("UPDATE pedidos SET estado = 'Despachado' WHERE id = %s", (id,), commit=True)
    log_auditoria(session['username'], 'UPDATE', 'pedidos', id, 'Pedido despachado')
    flash('Pedido marcado como despachado.', 'success')
    return redirect(url_for('distribuidores.index'))