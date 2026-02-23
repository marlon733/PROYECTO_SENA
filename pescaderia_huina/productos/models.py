from django.db import models

TIPO_PRODUCTO = [
    ('MA', 'Mariscos'),
    ('PE', 'Pescado'),
    ('PO', 'Pollo'),
]

TIPO_PRESENTACION = [
    ('VAC', 'Empacado al Vacío (Unidades)'),
    ('BAN', 'Bandeja (Unidades)'),
    ('LIB', 'A granel (Libras)'),
]

pedido = models.ForeignKey('pedidos.Pedido', on_delete=models.PROTECT, related_name='productos')

class Producto(models.Model):
    tipo_producto = models.CharField(max_length=3, choices=TIPO_PRODUCTO, default='PE')
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    tipo_presentacion = models.CharField(max_length=3, choices=TIPO_PRESENTACION)
    estado = models.BooleanField(default=True)
    

    def __str__(self):
        return self.nombre
