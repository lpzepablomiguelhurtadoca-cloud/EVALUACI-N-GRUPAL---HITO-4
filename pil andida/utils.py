from flask import request, session
from db import execute_query
import logging

logging.basicConfig(level=logging.INFO)

def log_auditoria(usuario, accion, tabla_afectada=None, registro_id=None, detalles=None):
    """Registra en la tabla logs_auditoria cada acción importante."""
    ip = request.remote_addr if request else '0.0.0.0'
    query = """
        INSERT INTO logs_auditoria (usuario, accion, tabla_afectada, registro_id, detalles, ip_address)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    execute_query(query, (usuario, accion, tabla_afectada, registro_id, detalles, ip), commit=True)

def obtener_metricas_dashboard():
    """Retorna un diccionario con las métricas clave para el dashboard."""
    metrics = {}
    # Total de unidades en stock
    query_stock = "SELECT SUM(cantidad) as total FROM stock"
    res = execute_query(query_stock, fetch_one=True)
    metrics['total_unidades'] = res['total'] if res['total'] else 0

    # Pedidos pendientes (Pendiente o Despachado)
    query_pedidos = "SELECT COUNT(*) as pendientes FROM pedidos WHERE estado IN ('Pendiente','Despachado')"
    metrics['pedidos_pendientes'] = execute_query(query_pedidos, fetch_one=True)['pendientes']

    # Lotes próximos a vencer (30 días)
    query_vencer = """
        SELECT COUNT(*) as por_vencer FROM lotes 
        WHERE fecha_vencimiento BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)
          AND control_calidad = 'Aprobado'
    """
    metrics['lotes_por_vencer'] = execute_query(query_vencer, fetch_one=True)['por_vencer']

    # Alertas de stock mínimo en los últimos 7 días
    query_alertas = "SELECT COUNT(*) as alertas FROM alertas_inventario WHERE fecha >= CURDATE() - INTERVAL 7 DAY"
    metrics['alertas_recientes'] = execute_query(query_alertas, fetch_one=True)['alertas']

    # Plantas activas (con al menos una bodega)
    query_plantas = "SELECT COUNT(DISTINCT planta_id) as plantas FROM bodegas"
    metrics['plantas_activas'] = execute_query(query_plantas, fetch_one=True)['plantas']

    return metrics