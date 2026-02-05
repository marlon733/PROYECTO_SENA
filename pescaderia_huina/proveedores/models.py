from django.db import models

class Proveedor(models.Model):
    # Identificación
    nit = models.CharField(max_length=20, unique=True, verbose_name="NIT/RUC")
    nombre_contacto = models.CharField(max_length=100, verbose_name="Nombre del Contacto")
    
    # Contacto
    correo = models.EmailField(max_length=100, verbose_name="Correo Electrónico")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono/Celular")
    direccion = models.CharField(max_length=255, verbose_name="Dirección")
    ciudad = models.CharField(max_length=100, verbose_name="Ciudad")
    
    # Información de negocio
    estado = models.BooleanField(default=True, verbose_name="Activo")
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"

    def __str__(self):
        return f"{self.nit}"
    