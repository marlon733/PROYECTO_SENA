from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone

class Venta(models.Model):
    ESTADOS = [
        ('COMPLETADA', 'Completada'),
        ('CANCELADA', 'Cancelada'),
        ('PENDIENTE', 'Pendiente'),
    ]
    
    TIPO_PRESENTACION= [
        ('EMPACADO_VACIO', 'Empacado al Vacío'),
        ('POR_LIBRA', 'Por Libra'),
        ('BANDEJA', 'Bandeja'),
    ]
    
    
    # Cliente
    nombre_cliente = models.CharField(max_length=100, null=True, blank=True)
    documento_cliente = models.CharField(max_length=20, null=True, blank=True)
    
    producto = models.ForeignKey(
    'productos.Producto', 
    on_delete=models.PROTECT,
    related_name='ventas',
    null=True,
    blank=True
)
    cantidad = models.PositiveSmallIntegerField(default=1)
    
    precio_unitario = models.DecimalField(
    max_digits=10, 
    decimal_places=2,
    null=True,
    blank=True,
    validators=[MinValueValidator(Decimal('0.01'))]
)
    
    # Detalles de la venta
    fecha_venta = models.DateTimeField(default=timezone.now)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    total = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    observaciones = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='COMPLETADA')
    tipo_presentacion = models.CharField(max_length=20, choices=TIPO_PRESENTACION, default='BANDEJA')
    
    # Campos para cancelación
    motivo_cancelacion = models.TextField(blank=True, null=True)
    fecha_cancelacion = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-fecha_venta']
    
    def __str__(self):
        return f"Venta #{self.id} - {self.nombre_cliente} - ${self.total}"
    
    def save(self, *args, **kwargs):
        # Calcular el total automáticamente
        if self.cantidad and self.precio_unitario:
            self.total = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
    
    def get_cliente_completo(self):
        """Método para obtener el nombre y documento del cliente"""
        return f"{self.nombre_cliente} - {self.documento_cliente}"
    
    def get_info_venta(self):
        """Método para obtener información resumida de la venta"""
        return f"Venta #{self.id} - {self.producto.nombre} x {self.cantidad}"