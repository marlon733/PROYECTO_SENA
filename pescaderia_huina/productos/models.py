from django.db import models
TIPO_PRODUCTO = [
        ('MA', 'Mariscos'),
        ('PE', 'Pescado'),
        ('PO', 'Pollo'),
    ]
class Producto(models.Model):
    tipo_producto = models.CharField(max_length=3, choices=TIPO_PRODUCTO, default='MA')
    nombre = models.CharField(max_length=100)
    procedencia = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10,decimal_places=2)
    tipo_prestacion = models.CharField(max_length=100)
    peso = models.DecimalField(max_digits=10,decimal_places=2)
    estado = models.BooleanField(default=True)
    stock = models.IntegerField(default=0)
# Create your models here.

    def __str__(self):
        return f"{self.nombre} {self.procedencia} - {self.documento_identidad}"
    def get_full_name(self):
        return f"{self.nombre} {self.apellido}"
