import mysql.connector
from mysql.connector import Error
from config import Config
import logging

logging.basicConfig(level=logging.INFO)

def get_db_connection():
    """Retorna una conexión a MySQL con manejo de errores."""
    try:
        conn = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DATABASE,
            port=Config.MYSQL_PORT,
            autocommit=False
        )
        return conn
    except Error as e:
        logging.error(f"Error conectando a MySQL: {e}")
        return None

def execute_query(query, params=None, fetch_one=False, fetch_all=False, commit=False):
    """
    Ejecuta una consulta parametrizada de forma segura (protección SQL Injection).
    """
    conn = get_db_connection()
    if not conn:
        return None
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        if commit:
            conn.commit()
            last_id = cursor.lastrowid
            cursor.close()
            conn.close()
            return last_id
        if fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
        else:
            result = None
        cursor.close()
        conn.close()
        return result
    except Error as e:
        logging.error(f"Error ejecutando query: {e}\nQuery: {query}\nParams: {params}")
        if conn:
            conn.rollback()
        cursor.close()
        conn.close()
        return None