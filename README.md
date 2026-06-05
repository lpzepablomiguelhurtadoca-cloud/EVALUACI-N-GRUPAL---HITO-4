# EVALUACI-N-GRUPAL---HITO-4

## Integrantes:
* Antezana Apaza Cristian
* Apaza Plata Leonardo Daniel
* Hurtado Castillo Pablo Miguel

## Descripción del proyecto:
Este proyecto consiste en el diseño e implementación de un Sistema Integral de Gestión de Inventarios y Control de Distribución para la Cervecería Boliviana Nacional.

El objetivo es automatizar y unificar el flujo del suministro que se gestionaba aparte. La solución viene desde el ingreso de la producción en las plantas nacionales (La Paz, Cochabamba y Santa Cruz) hasta el despacho final a los distribuidores autorizados.

## Instrucciones de Instalación

Encender Servicios: Abra XAMPP e inicie los módulos de Apache y MySQL. Importe el archivo base dentro de su gestor phpMyAdmin en una base de datos limpia.

Ubicarse en el Directorio: Abra la terminal de VS Code y desplácese con el comando cd hasta la carpeta interna del proyecto donde se encuentra alojado el script de arranque principal:

cd "pil andida"

Activar Entorno e Instalar Librerías: Encienda el entorno virtual de Python ejecutable en su terminal (.\venv\Scripts\activate) e instale en un solo bloque todas las dependencias requeridas del sistema con el siguiente comando:

pip install Flask mysql-connector-python pandas openpyxl reportlab

Lanzar la Aplicación: Ejecute el comando inicializador del servidor 

python app.py

Abra su navegador y entre a la dirección web local: http://127.0.0.1:5000.
## Credenciales de Acceso
admin contraseña: admin123