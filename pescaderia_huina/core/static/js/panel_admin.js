/* static/js/admin_main.js */

document.addEventListener("DOMContentLoaded", function() {

    // ==========================================
    // 1. GESTIÓN DEL SIDEBAR (Unificado)
    // ==========================================
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const mainContent = document.getElementById('main-content');

    if (sidebar && sidebarToggle && mainContent) {

        // --- A. Restaurar estado desde LocalStorage (Solo Desktop) ---
        const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
        if (window.innerWidth > 992 && isCollapsed) {
            sidebar.classList.add('collapsed');
            mainContent.classList.add('expanded');
        }

        // --- B. Lógica del Botón Toggle ---
        sidebarToggle.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevenir burbujeo
            
            if (window.innerWidth > 992) {
                // Modo Desktop: Colapsar/Expandir
                sidebar.classList.toggle('collapsed');
                mainContent.classList.toggle('expanded');
                
                // Guardar preferencia
                localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
            } else {
                // Modo Móvil: Mostrar/Ocultar (Overlay)
                sidebar.classList.toggle('mobile-active');
            }
        });

        // --- C. Cerrar al hacer click fuera (Solo Móvil) ---
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 992 && 
                sidebar.classList.contains('mobile-active') &&
                !sidebar.contains(e.target) && 
                !sidebarToggle.contains(e.target)) {
                
                sidebar.classList.remove('mobile-active');
            }
        });

        // --- D. Manejo de Resize (Limpieza de clases) ---
        window.addEventListener('resize', () => {
            if (window.innerWidth > 992) {
                // Si pasamos a desktop, quitamos la clase móvil
                sidebar.classList.remove('mobile-active');
                
                // Restauramos el estado colapsado si estaba guardado
                const shouldBeCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
                if (shouldBeCollapsed) {
                    sidebar.classList.add('collapsed');
                    mainContent.classList.add('expanded');
                } else {
                    sidebar.classList.remove('collapsed');
                    mainContent.classList.remove('expanded');
                }
            } else {
                // Si pasamos a móvil, quitamos las clases de desktop para evitar errores visuales
                sidebar.classList.remove('collapsed');
                mainContent.classList.remove('expanded');
            }
        });
    }

    // ==========================================
    // 2. UTILIDADES DE INTERFAZ
    // ==========================================

    // --- Marcar Link Activo en Sidebar ---
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.sidebar-nav .nav-link');
    
    navLinks.forEach(link => {
        // Comprobación exacta o si la URL contiene la ruta (para submenús)
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // --- Auto-cerrar Alertas (Toast/Messages) ---
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        // Solo auto-cerrar si es de éxito o info, dejar errores visibles más tiempo si se desea
        if (!alert.classList.contains('alert-danger')) {
            setTimeout(() => {
                // Verificar si bootstrap está disponible
                if (typeof bootstrap !== 'undefined') {
                    const bsAlert = new bootstrap.Alert(alert);
                    bsAlert.close();
                } else {
                    alert.style.display = 'none';
                }
            }, 5000); // 5 segundos
        }
    });

    // --- Tooltips de Bootstrap (Inicialización) ---
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // --- Búsqueda en Tiempo Real (Placeholder) ---
    const searchInput = document.querySelector('.search-box input');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            // Aquí puedes agregar lógica para filtrar tablas o hacer peticiones AJAX
            // console.log('Buscando:', searchTerm); 
        });
    }

    // ==========================================
    // 3. CONFIRMACIONES Y GRÁFICOS
    // ==========================================

    // --- Confirmación genérica de eliminación ---
    // Busca cualquier botón con el atributo data-confirm-delete
    const deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('¿Estás seguro de que deseas eliminar este elemento? Esta acción no se puede deshacer.')) {
                e.preventDefault();
            }
        });
    });

    // --- Inicializador de Gráficos (Helper para Chart.js) ---
    // Se adjunta a window para poder llamarlo desde los templates
    window.initDashboardChart = function(canvasId, data, options) {
        const ctx = document.getElementById(canvasId);
        if (ctx && typeof Chart !== 'undefined') {
            return new Chart(ctx, {
                type: data.type || 'bar',
                data: data,
                options: options || { responsive: true, maintainAspectRatio: false }
            });
        }
    };

    console.log('Panel Administrativo Huina: Inicializado');
});

// ==========================================
// 4. FUNCIONES GLOBALES (Expuestas a Window)
// ==========================================

/**
 * Muestra una notificación flotante en la interfaz
 * @param {string} message - El mensaje a mostrar
 * @param {string} type - 'success', 'danger', 'warning', 'info'
 */
window.showNotification = function(message, type = 'info') {
    // Buscar contenedor existente o crear uno
    let messagesContainer = document.querySelector('.messages-container');
    
    if (!messagesContainer) {
        // Si no existe un contenedor específico, usar el wrapper principal o crear uno flotante
        const wrapper = document.querySelector('.content-wrapper') || document.body;
        messagesContainer = document.createElement('div');
        messagesContainer.className = 'position-fixed top-0 end-0 p-3 messages-container';
        messagesContainer.style.zIndex = '1100';
        messagesContainer.style.marginTop = '80px'; // Ajuste por el topbar
        wrapper.appendChild(messagesContainer);
    }

    const alertDiv = document.createElement('div');
    // Iconos basados en el tipo
    let icon = 'info-circle-fill';
    if (type === 'success') icon = 'check-circle-fill';
    if (type === 'danger') icon = 'exclamation-circle-fill';
    if (type === 'warning') icon = 'exclamation-triangle-fill';

    alertDiv.className = `alert alert-${type} alert-dismissible fade show shadow-lg border-0 d-flex align-items-center mb-2`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        <i class="bi bi-${icon} fs-4 me-3"></i>
        <div>${message}</div>
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    messagesContainer.appendChild(alertDiv);
    
    // Auto-cerrar notificación dinámica
    setTimeout(() => {
        if (typeof bootstrap !== 'undefined') {
            const bsAlert = new bootstrap.Alert(alertDiv);
            bsAlert.close();
        } else {
            alertDiv.remove();
        }
    }, 5000);
};

/**
 * Wrapper simple para confirmaciones
 */
window.confirmAction = function(message) {
    return confirm(message || '¿Estás seguro de realizar esta acción?');
};