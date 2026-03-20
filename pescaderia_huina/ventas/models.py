from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone

IVA_PORCENTAJE = Decimal('0.19')  # 19% IVA Colombia


class Venta(models.Model):
    ESTADOS = [
        ('COMPLETADA', 'Completada'),
        ('CANCELADA', 'Cancelada'),
        ('PENDIENTE', 'Pendiente'),
    ]

    TIPO_PRESENTACION = [
        ('EMPACADO_VACIO', 'Empacado al Vacío'),
        ('POR_LIBRA', 'Por Libra'),
        ('BANDEJA', 'Bandeja'),
    ]

    # Información del cliente 
    nombre_cliente = models.CharField(max_length=100, null=True, blank=True, verbose_name='Nombre del Cliente')
    documento_cliente = models.CharField(max_length=20, null=True, blank=True, verbose_name='Documento')

    
    producto = models.ForeignKey(
        'productos.Producto',
        on_delete=models.PROTECT,
        related_name='ventas',
        null=True, blank=True
    )
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, default=1, null=True, blank=True)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal('0.01'))])
    tipo_presentacion = models.CharField(max_length=20, choices=TIPO_PRESENTACION, default='BANDEJA', null=True, blank=True)

    # Campos de iva y totales
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Subtotal')
    iva_monto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='IVA (19%)')
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal('0.01'))], verbose_name='Total')

    fecha_venta = models.DateTimeField(default=timezone.now)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    observaciones = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='COMPLETADA')

    motivo_cancelacion = models.TextField(blank=True, null=True)
    fecha_cancelacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-fecha_venta']

    def __str__(self):
        return f"Venta #{self.id} - {self.nombre_cliente or 'Anónimo'} - ${self.total}"

    def recalcular_totales(self):
        items = self.items.all()
        if items.exists():
            subtotal = sum(item.subtotal or Decimal('0') for item in items)
        elif self.cantidad and self.precio_unitario:
            subtotal = Decimal(str(self.cantidad)) * Decimal(str(self.precio_unitario))
        else:
            subtotal = Decimal('0')

        self.subtotal = subtotal
        self.iva_monto = (subtotal * IVA_PORCENTAJE).quantize(Decimal('0.01'))
        self.total = (subtotal + self.iva_monto).quantize(Decimal('0.01'))
        Venta.objects.filter(pk=self.pk).update(
            subtotal=self.subtotal,
            iva_monto=self.iva_monto,
            total=self.total
        )

    def get_cliente_display(self):
        return self.nombre_cliente or 'Cliente anónimo'


# múltiples productos por venta
class VentaItem(models.Model):
    TIPO_PRESENTACION = [
        ('EMPACADO_VACIO', 'Empacado al Vacío'),
        ('POR_LIBRA', 'Por Libra'),
        ('BANDEJA', 'Bandeja'),
    ]

    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey('productos.Producto', on_delete=models.CASCADE, verbose_name='Producto')
    tipo_presentacion = models.CharField(max_length=20, choices=TIPO_PRESENTACION, default='BANDEJA')
    cantidad = models.DecimalField(max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))], verbose_name='Cantidad')
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))], verbose_name='Precio Unitario')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = 'Ítem de Venta'
        verbose_name_plural = 'Ítems de Venta'

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"

    def save(self, *args, **kwargs):
        self.subtotal = (Decimal(str(self.cantidad)) * Decimal(str(self.precio_unitario))).quantize(Decimal('0.01'))
        super().save(*args, **kwargs)
    