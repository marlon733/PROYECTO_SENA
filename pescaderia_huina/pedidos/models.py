from django.db import models
from proveedores.models import Proveedor  
from productos.models import Producto     


class Pedido(models.Model):
    ESTADOS_CHOICES = [
        ('PEN', 'Pendiente'),
        ('REC', 'Recibido'),
        ('CAN', 'Cancelado'),
    ]

    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.CASCADE,
        verbose_name="Proveedor"
    )
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    estado = models.CharField(max_length=3, choices=ESTADOS_CHOICES, default='PEN')
    valor_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):

        return f"Pedido #{self.id} - {self.proveedor.nombre_contacto}"

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    presentacion = models.CharField(max_length=20, default='unidades', blank=True, null=True)
    precio_unitario = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Precio de compra al proveedor"
    )

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.producto.nombre} (x{self.cantidad})"