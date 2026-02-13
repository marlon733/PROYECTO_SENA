from django.db import models

class Proveedor(models.Model):
    # Opciones para el tipo de persona
    TIPO_PERSONA_CHOICES = [
        ('natural', 'Persona Natural'),
        ('juridica', 'Persona Jurídica'),
    ]

    tipo_persona = models.CharField(
        max_length=10,
        choices=TIPO_PERSONA_CHOICES,
        default='juridica',
        verbose_name="Tipo de Persona"
    )

    # Identificación (Ya era único, le agregamos mensaje personalizado)
    nit = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name="Identificación (NIT/Cédula)",
        error_messages={'unique': "Ya existe un proveedor registrado con este NIT o Cédula."}
    )
    
    nombre_contacto = models.CharField(max_length=100, verbose_name="Nombre del Contacto")
    
    # --- CAMBIOS AQUÍ ---
    correo = models.EmailField(
        max_length=100, 
        verbose_name="Correo Electrónico",
        unique=True,  # Esto impide repetidos
        error_messages={'unique': "Este correo electrónico ya está en uso por otro proveedor."}
    )
    
    telefono = models.CharField(
        max_length=20, 
        verbose_name="Teléfono/Celular",
        unique=True,  # Esto impide repetidos
        error_messages={'unique': "Este número de teléfono ya se encuentra registrado."}
    )
    # --------------------

    direccion = models.CharField(max_length=255, verbose_name="Dirección")
    ciudad = models.CharField(max_length=100, verbose_name="Ciudad")
    
    estado = models.BooleanField(default=True, verbose_name="Activo")
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"

    def __str__(self):
        return f"{self.nombre_contacto} ({self.nit})"