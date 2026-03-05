document.getElementById("resetForm").addEventListener("submit", function(event){
        event.preventDefault();
        const email = document.getElementById("email").value;

        // Aquí podrías enviar el correo al backend usando fetch o AJAX
        console.log("Correo ingresado: " + email);

        // Mostrar mensaje de éxito simulado
        document.getElementById("successMsg").style.display = "block";
    });