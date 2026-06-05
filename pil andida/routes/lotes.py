from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from auth import login_required
from db import execute_query
from utils import log_auditoria

bp = Blueprint('lotes', __name__, url_prefix='/lotes')

@bp.route('/')
@login_required()
def listar():
    search = request.args.get('search', '')
    planta = request.args.get('planta', '')
    query = """
        SELECT l.*, p.nombre_comercial, pl.nombre as planta_nombre
        FROM lotes l
        JOIN productos p ON l.producto_id = p.id
        JOIN plantas pl ON l.planta_id = pl.id
        WHERE 1=1
    """
    params = []
    if search:
        query += " AND l.numero_lote LIKE %s"
        params.append(f'%{search}%')
    if planta:
        query += " AND pl.nombre = %s"
        params.append(planta)
    query += " ORDER BY l.fecha_produccion DESC"
    lotes = execute_query(query, params, fetch_all=True)
    # Obtener lista de plantas y productos para los filtros
    plantas = execute_query("SELECT nombre FROM plantas", fetch_all=True)
    productos = execute_query("SELECT id, nombre_comercial, presentacion FROM productos ORDER BY nombre_comercial", fetch_all=True)
    return render_template('lotes.html', lotes=lotes, plantas=plantas, productos=productos, search=search, planta_filtro=planta)

@bp.route('/guardar', methods=['POST'])
@login_required(rol='admin')
def guardar():
    data = request.form
    # Mapear nombre de planta a ID
    planta_nombre = data['planta_origen']
    planta = execute_query("SELECT id FROM plantas WHERE nombre = %s", (planta_nombre,), fetch_one=True)
    if not planta:
        flash('Planta no válida.', 'danger')
        return redirect(url_for('lotes.listar'))
    
    query = """
        INSERT INTO lotes (numero_lote, producto_id, fecha_produccion, fecha_vencimiento, 
                           cantidad_producida, planta_id, control_calidad, tecnico_responsable, observaciones)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = (data['nro_lote'], data['producto_id'], data['fecha_produccion'],
              data['fecha_vencimiento'], data['cantidad'], planta['id'],
              data['calidad_resultado'], data.get('tecnico', ''), data.get('observaciones', ''))
    new_id = execute_query(query, params, commit=True)
    
    # Registrar entrada automática en stock si el lote está aprobado
    if data['calidad_resultado'] == 'Aprobado':
        # Buscar una bodega de "Producto Terminado" en la misma planta
        bodega = execute_query("""
            SELECT id FROM bodegas WHERE planta_id = %s AND tipo_bodega = 'Producto Terminado' LIMIT 1
        """, (planta['id'],), fetch_one=True)
        if bodega:
            # Llamar al procedimiento registrar_movimiento para ENTRADA
            execute_query("""
                CALL registrar_movimiento('ENTRADA', NULL, %s, %s, %s, %s, %s)
            """, (bodega['id'], new_id, data['cantidad'], session['username'], 'Producción inicial'), commit=True)
    
    log_auditoria(session['username'], 'CREATE', 'lotes', new_id, f'Creó lote {data["nro_lote"]}')
    flash('Lote registrado exitosamente.', 'success')
    return redirect(url_for('lotes.listar'))

@bp.route('/editar/<int:id>')
@login_required(rol='admin')
def editar(id):
    lote = execute_query("""
        SELECT l.*, p.nombre_comercial, pl.nombre as planta_nombre
        FROM lotes l
        JOIN productos p ON l.producto_id = p.id
        JOIN plantas pl ON l.planta_id = pl.id
        WHERE l.id = %s
    """, (id,), fetch_one=True)
    if not lote:
        flash('Lote no encontrado.', 'danger')
        return redirect(url_for('lotes.listar'))
    productos = execute_query("SELECT id, nombre_comercial FROM productos", fetch_all=True)
    plantas = execute_query("SELECT id, nombre FROM plantas", fetch_all=True)
    return render_template('lotes_editar.html', lote=lote, productos=productos, plantas=plantas)

@bp.route('/actualizar/<int:id>', methods=['POST'])
@login_required(rol='admin')
def actualizar(id):
    data = request.form
    query = """
        UPDATE lotes SET numero_lote=%s, producto_id=%s, fecha_produccion=%s, fecha_vencimiento=%s,
        cantidad_producida=%s, planta_id=%s, control_calidad=%s, tecnico_responsable=%s, observaciones=%s
        WHERE id=%s
    """
    params = (data['nro_lote'], data['producto_id'], data['fecha_produccion'],
              data['fecha_vencimiento'], data['cantidad'], data['planta_id'],
              data['calidad_resultado'], data.get('tecnico', ''), data.get('observaciones', ''), id)
    execute_query(query, params, commit=True)
    log_auditoria(session['username'], 'UPDATE', 'lotes', id, f'Actualizó lote ID {id}')
    flash('Lote actualizado.', 'success')
    return redirect(url_for('lotes.listar'))

@bp.route('/eliminar/<int:id>')
@login_required(rol='admin')
def eliminar(id):
    # Verificar que no tenga movimientos asociados
    movs = execute_query("SELECT COUNT(*) as total FROM movimientos WHERE lote_id = %s", (id,), fetch_one=True)
    if movs['total'] > 0:
        flash('No se puede eliminar un lote con movimientos registrados.', 'danger')
        return redirect(url_for('lotes.listar'))
    execute_query("DELETE FROM lotes WHERE id = %s", (id,), commit=True)
    log_auditoria(session['username'], 'DELETE', 'lotes', id, f'Eliminó lote ID {id}')
    flash('Lote eliminado.', 'success')
    return redirect(url_for('lotes.listar'))