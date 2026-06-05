import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-super-segura-cerveceria-2026'
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'       # Usuario con privilegios mínimos
    MYSQL_PASSWORD = ''
    MYSQL_DATABASE = 'cerveceria_boliviana'
    MYSQL_PORT = 3306

    # Carpeta para backups
    BACKUP_FOLDER = 'backups'
    if not os.path.exists(BACKUP_FOLDER):
        os.makedirs(BACKUP_FOLDER)