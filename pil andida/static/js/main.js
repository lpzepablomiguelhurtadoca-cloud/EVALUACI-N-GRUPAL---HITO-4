/**
 * PIL ANDINA - Sistema de Gestión de Inventario y Distribución
 * Script Principal - Funcionalidades Comunes
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips y funcionalidades generales
    initializeAlerts();
    initializeSystemTime();
    initializeSidebarActive();
});

/**
 * Inicializar alertas con cierre automático
 */
function initializeAlerts() {
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(alert => {
        // Auto-cerrar después de 5 segundos (excepto alertas de error)
        if (!alert.classList.contains('alert-danger')) {
            setTimeout(() => {
                alert.style.opacity = '0';
                alert.style.transition = 'opacity 0.3s ease';
                setTimeout(() => alert.remove(), 300);
            }, 5000);
        }
    });
}

/**
 * Actualizar hora del sistema en tiempo real
 */
function initializeSystemTime() {
    const systemTimeEl = document.getElementById('system-time');
    if (systemTimeEl) {
        function updateTime() {
            const now = new Date();
            systemTimeEl.textContent = now.toLocaleString('es-BO', {
                weekday: 'short',
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
        }
        
        updateTime();
        setInterval(updateTime, 1000);
    }
}

/**
 * Marcar el enlace activo en la barra lateral
 */
function initializeSidebarActive() {
    const currentUrl = window.location.pathname;
    const sidebarLinks = document.querySelectorAll('.sidebar-nav a');
    
    sidebarLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentUrl || (href === '/dashboard' && currentUrl === '/')) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

/**
 * Formatear moneda en Bolivianos
 */
function formatCurrency(value) {
    return new Intl.NumberFormat('es-BO', {
        style: 'currency',
        currency: 'BOB'
    }).format(value);
}

/**
 * Formatear fecha en formato legible
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-BO', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

/**
 * Mostrar confirmación antes de eliminar
 */
function confirmDelete(message = '¿Está seguro que desea eliminar este registro?') {
    return confirm(message);
}

/**
 * Validar formulario antes de enviar
 */
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    
    for (let input of inputs) {
        if (!input.value.trim()) {
            input.focus();
            input.style.borderColor = 'var(--danger)';
            showToast('Por favor complete todos los campos requeridos', 'error');
            return false;
        } else {
            input.style.borderColor = '';
        }
    }
    
    return true;
}

/**
 * Mostrar notificación tipo toast
 */
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type}`;
    toast.innerHTML = `
        <span>${message}</span>
        <span class="alert-close" onclick="this.parentElement.remove();">×</span>
    `;
    
    const mainContent = document.getElementById('main-content');
    if (mainContent) {
        mainContent.insertBefore(toast, mainContent.firstChild);
        
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transition = 'opacity 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

/**
 * Exportar tabla a CSV
 */
function exportTableToCSV(tableId, filename = 'export.csv') {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    let csv = [];
    const rows = table.querySelectorAll('tr');
    
    rows.forEach(row => {
        const cols = row.querySelectorAll('td, th');
        const csvrow = [];
        
        cols.forEach(col => {
            csvrow.push('"' + col.innerText + '"');
        });
        
        csv.push(csvrow.join(','));
    });
    
    downloadCSV(csv.join('\n'), filename);
}

/**
 * Descargar CSV
 */
function downloadCSV(csv, filename) {
    const link = document.createElement('a');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    link.setAttribute('href', URL.createObjectURL(blob));
    link.setAttribute('download', filename);
    link.click();
}

/**
 * Imprimir documento
 */
function printDocument() {
    window.print();
}

/**
 * Buscar en tabla
 */
function searchTable(searchInputId, tableId) {
    const searchInput = document.getElementById(searchInputId);
    const table = document.getElementById(tableId);
    
    if (!searchInput || !table) return;
    
    searchInput.addEventListener('keyup', function() {
        const search = this.value.toLowerCase();
        const rows = table.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
            row.style.display = row.innerText.toLowerCase().includes(search) ? '' : 'none';
        });
    });
}

/**
 * Crear gráfico simple
 */
function createSimpleChart(canvasId, labels, data, label = 'Datos') {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    // Implementación simple sin Chart.js
    const ctx = canvas.getContext('2d');
    const maxValue = Math.max(...data);
    const barWidth = canvas.width / labels.length;
    
    labels.forEach((label, i) => {
        const height = (data[i] / maxValue) * (canvas.height - 20);
        ctx.fillStyle = '#d4a574';
        ctx.fillRect(i * barWidth, canvas.height - height, barWidth - 10, height);
        ctx.fillStyle = '#cbd5e1';
        ctx.font = '12px Inter';
        ctx.textAlign = 'center';
        ctx.fillText(label, i * barWidth + barWidth / 2, canvas.height);
    });
}

/**
 * Enviar formulario con validación
 */
function submitFormWithValidation(event, formId) {
    event.preventDefault();
    
    if (validateForm(formId)) {
        document.getElementById(formId).submit();
    }
}

/**
 * Cargar contenido dinámicamente
 */
function loadContent(url, targetId) {
    const target = document.getElementById(targetId);
    if (!target) return;
    
    fetch(url)
        .then(response => response.text())
        .then(html => {
            target.innerHTML = html;
        })
        .catch(error => {
            console.error('Error cargando contenido:', error);
            showToast('Error al cargar el contenido', 'danger');
        });
}

/**
 * Marcar todos los checkboxes
 */
function toggleAllCheckboxes(checkboxId) {
    const checkbox = document.getElementById(checkboxId);
    if (!checkbox) return;
    
    const allCheckboxes = document.querySelectorAll('input[type="checkbox"]:not(#' + checkboxId + ')');
    allCheckboxes.forEach(cb => cb.checked = checkbox.checked);
}

/**
 * Recargar página
 */
function reloadPage() {
    location.reload();
}

/**
 * Redirigir a URL
 */
function redirectTo(url) {
    window.location.href = url;
}
