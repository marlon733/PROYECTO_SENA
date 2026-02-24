from django.db import models

class Proveedor(models.Model):
    # Opciones
    TIPO_PERSONA_CHOICES = [
        ('natural', 'Persona Natural'),
        ('juridica', 'Persona Jurídica'),
    ]

    # Campos
    tipo_persona = models.CharField(
        max_length=10,
        choices=TIPO_PERSONA_CHOICES,
        default='juridica',
        verbose_name="Tipo de Persona"
    )

    nit = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name="Identificación (NIT/Cédula)",
        error_messages={'unique': "Ya existe un proveedor con este NIT o Cédula."}
    )
    
    nombre_contacto = models.CharField(max_length=100, verbose_name="Nombre del Contacto/Empresa")
    
    correo = models.EmailField(
        max_length=100, 
        unique=True,
        verbose_name="Correo Electrónico",
        error_messages={'unique': "Este correo ya está registrado."}
    )
    
    telefono = models.CharField(
        max_length=20, 
        unique=True,
        verbose_name="Teléfono",
        error_messages={'unique': "Este teléfono ya está registrado."}
    )

    direccion = models.CharField(max_length=255, verbose_name="Dirección")
    ciudad = models.CharField(max_length=100, verbose_name="Ciudad")
    
    estado = models.BooleanField(default=True, verbose_name="Activo")
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['-fecha_registro'] # Ordena del más nuevo al más viejo

    def __str__(self):
        return f"{self.nombre_contacto} ({self.nit})"