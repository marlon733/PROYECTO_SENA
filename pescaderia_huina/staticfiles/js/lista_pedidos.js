
    document.addEventListener("DOMContentLoaded", function() {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl)
        });

        // --- LÓGICA FETCH CON SWEETALERT2 ---
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }

        const botonesEstado = document.querySelectorAll('.btn-cambiar-estado');

        botonesEstado.forEach(boton => {
            boton.addEventListener('click', function(e) {
                e.preventDefault();
                const pedidoId = this.getAttribute('data-id');
                const nuevoEstado = this.getAttribute('data-estado');
                
                // Configuramos los textos y colores dinámicamente según el botón que se presionó
                const esRecibido = nuevoEstado === 'recibido';
                const tituloAlert = esRecibido ? '¿Marcar como RECIBIDO?' : '¿CANCELAR pedido?';
                const textoAlert = esRecibido ? 'Confirma que el proveedor entregó la mercancía.' : 'Esta acción anulará la orden de compra.';
                const iconoAlert = esRecibido ? 'success' : 'warning';
                const colorBoton = esRecibido ? '#198754' : '#dc3545';
                const textoBoton = esRecibido ? 'Sí, recibir pedido' : 'Sí, cancelar pedido';

                // Usamos SweetAlert en lugar del confirm() nativo
                Swal.fire({
                    title: tituloAlert,
                    text: textoAlert,
                    icon: iconoAlert,
                    showCancelButton: true,
                    confirmButtonColor: colorBoton,
                    cancelButtonColor: '#6c757d',
                    confirmButtonText: textoBoton,
                    cancelButtonText: 'No, regresar',
                    reverseButtons: true, // Pone el botón de cancelar a la izquierda
                    customClass: { popup: 'rounded-4 shadow' } // Bordes redondeados modernos
                }).then((result) => {
                    if (result.isConfirmed) {
                        
                        // Si el usuario confirma, hacemos la petición a Django
                        fetch(`/pedidos/cambiar-estado/${pedidoId}/`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': getCookie('csrftoken')
                            },
                            body: JSON.stringify({ 'estado': nuevoEstado })
                        })
                        .then(response => response.json())
                        .then(data => {
                            if(data.success) {
                                // Alerta bonita de éxito antes de recargar
                                Swal.fire({
                                    title: '¡Actualizado!',
                                    text: 'El estado se guardó correctamente.',
                                    icon: 'success',
                                    timer: 1500,
                                    showConfirmButton: false
                                }).then(() => {
                                    window.location.reload(); 
                                });
                            } else {
                                Swal.fire('Error', 'Hubo un problema: ' + (data.error || 'Desconocido'), 'error');
                            }
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            Swal.fire('Error', 'Hubo un error de conexión con el servidor.', 'error');
                        });
                    }
                });
            });
        });
    });

    const formatter = new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    });

    document.querySelectorAll('.money-format').forEach(el => {
        const value = parseFloat(el.innerText);
        if (!isNaN(value)) {
            el.innerText = formatter.format(value).replace(/\s+/g, '');
        }
    });

