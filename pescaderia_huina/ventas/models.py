from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

# Modelo de Producto (simplificado - debería estar en otro módulo)
class Producto(models.Model):
    """
    Modelo de Producto basado en Historia de Usuario #1
    Registra nombre, unidad de medida, precio base y otros atributos
    """
    UNIDAD_MEDIDA_CHOICES = [
        ('KG', 'Kilogramo'),
        ('UNIDAD', 'Unidad'),
        ('LB', 'Libra'),
        ('DOCENA', 'Docena'),
    ]
    
    nombre = models.CharField(max_length=200, unique=True)
    unidad_medida = models.CharField(max_length=10, choices=UNIDAD_MEDIDA_CHOICES, default='UNIDAD')
    precio_base = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    cantidad_disponible = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0'))])
    fecha_caducidad = models.DateField(null=True, blank=True)
    costo_unitario_compra = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} - {self.get_unidad_medida_display()}"
    
    def stock_disponible(self):
        """Retorna la cantidad disponible en formato legible"""
        return f"{self.cantidad_disponible} {self.get_unidad_medida_display()}"
    
    def margen_ganancia(self):
        """Calcula el margen de ganancia del producto (Historia #14)"""
        if self.costo_unitario_compra > 0:
            margen = ((self.precio_base - self.costo_unitario_compra) / self.costo_unitario_compra) * 100
            return round(margen, 2)
        return 0


class Venta(models.Model):
    """
    Modelo de Venta basado en Historia de Usuario #10, #11, #12
    Registra las ventas al detalle con productos y cantidades
    """
    ESTADO_CHOICES = [
        ('COMPLETADA', 'Completada'),
        ('CANCELADA', 'Cancelada'),
        ('PENDIENTE', 'Pendiente'),
    ]
    
    fecha_venta = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0'))])
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='COMPLETADA')
    observaciones = models.TextField(null=True, blank=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-fecha_venta']
    
    def __str__(self):
        return f"Venta #{self.id} - {self.fecha_venta.strftime('%d/%m/%Y %H:%M')} - ${self.total}"
    
    def calcular_total(self):
        """Calcula el total de la venta sumando todos los detalles"""
        total = sum(detalle.subtotal for detalle in self.detalles.all())
        self.total = total
        self.save()
        return total
    
    def cancelar_venta(self):
        """
        Cancela la venta y revierte el stock (Historia #12)
        """
        if self.estado != 'CANCELADA':
            # Revertir el stock de cada producto
            for detalle in self.detalles.all():
                producto = detalle.producto
                producto.cantidad_disponible += detalle.cantidad
                producto.save()
            
            self.estado = 'CANCELADA'
            self.save()
            return True
        return False
    
    def cantidad_productos(self):
        """Retorna la cantidad de productos diferentes en la venta"""
        return self.detalles.count()


class DetalleVenta(models.Model):
    """
    Modelo de Detalle de Venta (Historia #10)
    Registra cada producto vendido con su cantidad y precio
    """
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    
    class Meta:
        verbose_name = 'Detalle de Venta'
        verbose_name_plural = 'Detalles de Venta'
    
    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad} {self.producto.get_unidad_medida_display()}"
    
    def save(self, *args, **kwargs):
        """Calcula el subtotal automáticamente antes de guardar"""
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
