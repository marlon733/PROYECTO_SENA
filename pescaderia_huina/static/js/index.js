    // Abrir y cerrar modal de login
    function abrirModalLogin() {
      document.getElementById("modalLogin").style.display = "flex";
    }

    function cerrarModalLogin() {
      document.getElementById("modalLogin").style.display = "none";
    }

    // Abrir modal de mensajes
    function mostrarMensaje(texto, redirigir = false) {
      document.getElementById("mensajeTexto").innerText = texto;
      document.getElementById("modalMensaje").style.display = "flex";

      // Si debe redirigir (cuando se valida correctamente)
      if (redirigir) {
        document.getElementById("cerrarMensaje").onclick = function() {
          cerrarModalMensaje();
          window.location.href = 'registro.html';
        }
      }
    }

    // Cerrar modal de mensajes
    function cerrarModalMensaje() {
      document.getElementById("modalMensaje").style.display = "none";
    }

    // Validación de usuario y contraseña
    function validar() {
      let usuario = document.getElementById("usuario").value;
      let contraseña = document.getElementById("contraseña").value;

      if (usuario && contraseña) {
        if (usuario === "administrador" && contraseña === "admin123") {
          cerrarModalLogin();
          mostrarMensaje("¡Bienvenido, administrador!", true);
          window.location.href = 'registro.html';
        } else {
          mostrarMensaje("Acceso denegado");
        }
      } else {
        mostrarMensaje("Debes completar ambos campos.");
      }
    }