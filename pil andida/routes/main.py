from flask import Blueprint, render_template, session
from auth import login_required
from utils import obtener_metricas_dashboard
from db import execute_query

bp = Blueprint('main', __name__)

@bp.route('/dashboard')
@login_required()
def dashboard():
    metrics = obtener_metricas_dashboard()
    
    # Datos para el gráfico de rotación (últimos 6 meses, ejemplo)
    query_rotacion = """
        SELECT 
            DATE_FORMAT(m.fecha_movimiento, '%%Y-%%m') as mes,
            SUM(CASE WHEN m.tipo_movimiento = 'SALIDA' THEN m.cantidad ELSE 0 END) as salidas
        FROM movimientos m
        WHERE m.fecha_movimiento >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
        GROUP BY DATE_FORMAT(m.fecha_movimiento, '%%Y-%%m')
        ORDER BY mes ASC
    """
    datos_rotacion = execute_query(query_rotacion, fetch_all=True) or []
    
    # Preparar etiquetas y valores para el gráfico (se pasan al template)
    meses = [d['mes'] for d in datos_rotacion]
    ventas = [d['salidas'] for d in datos_rotacion]
    
    return render_template('dashboard.html', 
                           metrics=metrics, 
                           meses=meses, 
                           ventas=ventas,
                           username=session.get('username'),
                           rol=session.get('rol'))