from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from auth import login_required
from db import execute_query
from utils import log_auditoria

bp = Blueprint('inventario', __name__, url_prefix='/inventario')

@bp.route('/')
@login_required()
def index():
    query = """
        SELECT pl.nombre as planta, b.nombre_bodega, p.nombre_comercial, l.numero_lote, s.cantidad,
               p.stock_minimo, l.id as lote_id
        FROM stock s
        JOIN bodegas b ON s.bodega_id = b.id
        JOIN plantas pl ON b.planta_id = pl.id
        JOIN lotes l ON s.lote_id = l.id
        JOIN productos p ON l.producto_id = p.id
        WHERE l.control_calidad = 'Aprobado'
        ORDER BY pl.nombre, b.nombre_bodega
    """
    stock_data = execute_query(query, fetch_all=True)
    alertas = execute_query("SELECT * FROM alertas_inventario ORDER BY fecha DESC LIMIT 10", fetch_all=True)
    lotes = execute_query("""
        SELECT l.id, l.numero_lote, p.nombre_comercial, pl.nombre as planta
        FROM lotes l
        JOIN productos p ON l.producto_id = p.id
        JOIN plantas pl ON l.planta_id = pl.id
        WHERE l.control_calidad = 'Aprobado'
        ORDER BY l.id DESC
    """, fetch_all=True)
    return render_template('inventario.html', stock_data=stock_data, alertas=alertas, lotes=lotes)

@bp.route('/ajuste', methods=['POST'])
@login_required(rol='admin')
def ajuste():
    # Ahora esperamos un ID numérico (value="1" en el select)
    lote_id = request.form.get('lote_ajuste')
    tipo_ajuste = request.form.get('tipo_movimiento')
    cantidad = int(request.form.get('cantidad_ajuste'))
    autorizado = request.form.get('autorizado_por')
    
    # Validar que lote_id sea numérico
    if not lote_id or not lote_id.isdigit():
        flash('Lote inválido.', 'danger')
        return redirect(url_for('inventario.index'))
    lote_id = int(lote_id)
    
    bodega = execute_query("""
        SELECT bodega_id FROM stock WHERE lote_id = %s AND cantidad > 0 LIMIT 1
    """, (lote_id,), fetch_one=True)
    if not bodega:
        flash('El lote no tiene stock disponible en ninguna bodega.', 'danger')
        return redirect(url_for('inventario.index'))
    
    observacion = f"Ajuste por {tipo_ajuste}. Autorizado por: {autorizado}"
    execute_query("""
        CALL registrar_movimiento('SALIDA', %s, NULL, %s, %s, %s, %s)
    """, (bodega['bodega_id'], lote_id, cantidad, session['username'], observacion), commit=True)
    
    log_auditoria(session['username'], 'STOCK_ADJUST', 'stock', lote_id, observacion)
    flash(f'Ajuste aplicado: se descontaron {cantidad} unidades.', 'success')
    return redirect(url_for('inventario.index'))