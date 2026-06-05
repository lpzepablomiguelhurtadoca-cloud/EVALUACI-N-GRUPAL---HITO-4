from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from auth import login_required
from db import execute_query
from utils import log_auditoria

bp = Blueprint('plantas_bodegas', __name__, url_prefix='/bodegas')

@bp.route('/')
@login_required()
def index():
    return render_template('plantas.html')

@bp.route('/guardar', methods=['POST'])
@login_required(rol='admin')
def guardar():
    data = request.form
    query = """
        INSERT INTO bodegas (planta_id, nombre_bodega, tipo_bodega, ubicacion_fisica, capacidad_maxima, temperatura)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    # Generar nombre automático si no viene
    nombre_bodega = data.get('nombre_bodega') or f"Bodega {data['tipo_bodega']}"
    params = (data['planta_id'], nombre_bodega, data['tipo_bodega'], 
              data.get('ubicacion_fisica', ''), data.get('capacidad'), data.get('temperatura'))
    new_id = execute_query(query, params, commit=True)
    log_auditoria(session['username'], 'CREATE', 'bodegas', new_id, f'Creó bodega en planta {data["planta_id"]}')
    flash('Bodega registrada exitosamente.', 'success')
    return redirect(url_for('plantas_bodegas.index'))