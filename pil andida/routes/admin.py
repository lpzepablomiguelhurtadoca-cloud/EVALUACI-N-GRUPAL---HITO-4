from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
from auth import login_required
from db import execute_query
from utils import log_auditoria
import subprocess, os, glob, datetime
from config import Config

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/')
@login_required(rol='admin')
def index():
    # Obtener logs de auditoría para mostrar en la tabla
    logs = execute_query("SELECT * FROM logs_auditoria ORDER BY fecha DESC LIMIT 20", fetch_all=True)
    # Obtener lista de backups
    backups = []
    archivos = glob.glob(os.path.join(Config.BACKUP_FOLDER, '*.sql'))
    for f in archivos:
        stat = os.stat(f)
        backups.append({
            'nombre': os.path.basename(f),
            'fecha': datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            'tamano': f"{stat.st_size / (1024*1024):.2f} MB"
        })
    backups.sort(key=lambda x: x['fecha'], reverse=True)
    return render_template('admin.html', logs=logs, backups=backups)

@bp.route('/backup/crear', methods=['POST'])
@login_required(rol='admin')
def crear_backup():
    nombre = f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    ruta_completa = os.path.join(Config.BACKUP_FOLDER, nombre)
    cmd = f"mysqldump -h {Config.MYSQL_HOST} -u {Config.MYSQL_USER} -p{Config.MYSQL_PASSWORD} {Config.MYSQL_DATABASE} > {ruta_completa}"
    ret = subprocess.call(cmd, shell=True)
    if ret == 0:
        log_auditoria(session['username'], 'BACKUP_CREATE', detalles=f'Backup creado: {nombre}')
        flash('Backup generado exitosamente.', 'success')
    else:
        flash('Error al generar backup.', 'danger')
    return redirect(url_for('admin.index'))

@bp.route('/backup/restaurar/<nombre>', methods=['POST'])
@login_required(rol='admin')
def restaurar_backup(nombre):
    # Validar que el nombre no contenga path traversal
    if '..' in nombre or '/' in nombre:
        flash('Nombre de archivo inválido.', 'danger')
        return redirect(url_for('admin.index'))
    ruta = os.path.join(Config.BACKUP_FOLDER, nombre)
    if not os.path.exists(ruta):
        flash('Archivo no encontrado.', 'danger')
        return redirect(url_for('admin.index'))
    # Restaurar (peligroso, pedir confirmación en frontend)
    cmd = f"mysql -h {Config.MYSQL_HOST} -u {Config.MYSQL_USER} -p{Config.MYSQL_PASSWORD} {Config.MYSQL_DATABASE} < {ruta}"
    ret = subprocess.call(cmd, shell=True)
    if ret == 0:
        log_auditoria(session['username'], 'BACKUP_RESTORE', detalles=f'Restaurado backup: {nombre}')
        flash('Base de datos restaurada correctamente.', 'success')
    else:
        flash('Error al restaurar.', 'danger')
    return redirect(url_for('admin.index'))

@bp.route('/conexiones')
@login_required(rol='admin')
def conexiones():
    procesos = execute_query("SHOW PROCESSLIST", fetch_all=True)
    return jsonify({'conexiones_activas': len(procesos), 'detalle': procesos})

@bp.route('/slow-queries')
@login_required(rol='admin')
def slow_queries():
    try:
        with open('/var/log/mysql/slow-queries.log', 'r') as f:
            lines = f.readlines()[-50:]
        return jsonify({'slow_queries': lines})
    except:
        return jsonify({'error': 'Log de consultas lentas no disponible'}), 500