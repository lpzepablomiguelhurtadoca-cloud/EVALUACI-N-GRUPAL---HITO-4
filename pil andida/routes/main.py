from flask import Blueprint, render_template, session
from auth import login_required
from utils import obtener_metricas_dashboard
from db import execute_query

bp = Blueprint('main', __name__)

@bp.route('/dashboard')
@login_required()
def dashboard():
    # Métricas principales
    metrics = obtener_metricas_dashboard()

    # Consulta para rotación de inventario (últimos 6 meses)
    query_rotacion = """
        SELECT
            DATE_FORMAT(m.fecha_movimiento, '%%Y-%%m') AS mes,
            SUM(
                CASE
                    WHEN m.tipo_movimiento = 'SALIDA'
                    THEN m.cantidad
                    ELSE 0
                END
            ) AS salidas
        FROM movimientos m
        WHERE m.fecha_movimiento >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
        GROUP BY DATE_FORMAT(m.fecha_movimiento, '%%Y-%%m')
        ORDER BY mes ASC
    """

    datos_rotacion = execute_query(query_rotacion, fetch_all=True) or []

    # Preparar datos para la gráfica
    meses = [d['mes'] for d in datos_rotacion]
    ventas = [float(d['salidas'] or 0) for d in datos_rotacion]

    # Evitar división por cero en el template
    max_ventas = max(ventas) if ventas and max(ventas) > 0 else 1

    # Debug (opcional, puedes eliminarlo luego)
    print("DATOS ROTACION:", datos_rotacion)
    print("MESES:", meses)
    print("VENTAS:", ventas)
    print("MAX VENTAS:", max_ventas)

    return render_template(
        'dashboard.html',
        metrics=metrics,
        meses=meses,
        ventas=ventas,
        max_ventas=max_ventas,
        username=session.get('username'),
        rol=session.get('rol')
    )