from flask import Blueprint, render_template, request, Response, session, jsonify
from auth import login_required
from db import execute_query
import csv, io, pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

bp = Blueprint('reportes', __name__, url_prefix='/reportes')

@bp.route('/')
@login_required()
def index():
    return render_template('reportes.html')

@bp.route('/consultar', methods=['GET'])
@login_required()
def consultar():
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    producto_id = request.args.get('filtro_producto')
    
    query = """
        SELECT p.nombre_comercial, SUM(m.cantidad) as unidades, SUM(m.cantidad * pr.precio_actual) as total_recaudado,
               pl.nombre as planta
        FROM movimientos m
        JOIN lotes l ON m.lote_id = l.id
        JOIN productos p ON l.producto_id = p.id
        JOIN productos pr ON pr.id = p.id
        JOIN bodegas b ON COALESCE(m.bodega_origen_id, m.bodega_destino_id) = b.id
        JOIN plantas pl ON b.planta_id = pl.id
        WHERE m.tipo_movimiento = 'SALIDA'
          AND DATE(m.fecha_movimiento) BETWEEN %s AND %s
    """
    params = [fecha_inicio, fecha_fin]
    if producto_id and producto_id != 'todos':
        query += " AND p.id = %s"
        params.append(producto_id)
    query += " GROUP BY p.id, pl.id ORDER BY unidades DESC"
    
    resultados = execute_query(query, params, fetch_all=True)
    # Renderizar la misma página con los resultados
    return render_template('reportes.html', resultados=resultados, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)

@bp.route('/exportar/csv')
@login_required()
def exportar_csv():
    tipo = request.args.get('tipo', 'stock_planta')
    if tipo == 'stock_planta':
        query = "SELECT * FROM vista_stock_planta"
        filename = "reporte_stock_planta.csv"
    elif tipo == 'proximos_vencer':
        query = "SELECT * FROM vista_proximos_vencer"
        filename = "lotes_proximos_vencer.csv"
    else:
        return "Tipo no válido", 400
    
    data = execute_query(query, fetch_all=True)
    if not data:
        return "Sin datos", 404
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    
    return Response(output.getvalue(), mimetype='text/csv', 
                    headers={"Content-Disposition": f"attachment;filename={filename}"})

@bp.route('/exportar/excel')
@login_required()
def exportar_excel():
    tipo = request.args.get('tipo', 'stock_planta')
    query_map = {
        'stock_planta': "SELECT * FROM vista_stock_planta",
        'proximos_vencer': "SELECT * FROM vista_proximos_vencer",
        'pedidos_pendientes': "SELECT * FROM vista_pedidos_pendientes"
    }
    query = query_map.get(tipo)
    if not query:
        return "Tipo no válido", 400
    data = execute_query(query, fetch_all=True)
    if not data:
        return "Sin datos", 404
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Reporte', index=False)
    return Response(output.getvalue(), 
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    headers={"Content-Disposition": f"attachment;filename={tipo}.xlsx"})

@bp.route('/proximos-vencer/pdf')
@login_required()
def pdf_proximos_vencer():
    data = execute_query("SELECT * FROM vista_proximos_vencer", fetch_all=True)
    if not data:
        return "Sin datos", 404
    
    response = Response(content_type='application/pdf')
    response.headers['Content-Disposition'] = 'attachment; filename=proximos_vencer.pdf'
    
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    title = Paragraph("Lotes próximos a vencer", styles['Title'])
    elements.append(title)
    
    # Crear tabla
    table_data = [["N° Lote", "Producto", "Presentación", "Vencimiento", "Días restantes", "Stock"]]
    for row in data:
        table_data.append([
            row['numero_lote'], row['nombre_comercial'], row['presentacion'],
            str(row['fecha_vencimiento']), str(row['dias_restantes']), str(row['stock_disponible'])
        ])
    t = Table(table_data)
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.grey),
                           ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                           ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                           ('GRID', (0,0), (-1,-1), 1, colors.black)]))
    elements.append(t)
    doc.build(elements)
    return response