from django.db import models
# Asegúrate de que la importación apunte correctamente a tu app de proveedores
from proveedores.models import Proveedor 

class Producto(models.Model):
    # --- Opciones ---
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

    # --- RELACIÓN CON PROVEEDOR (Protegida) ---
    proveedor = models.ForeignKey(
        Proveedor, 
        on_delete=models.SET_NULL, # <--- CLAVE: Si borras el proveedor, el producto queda huerfano pero existe
        null=True,                 # Permite guardar sin proveedor
        blank=True,                
        related_name='productos', 
        verbose_name="Proveedor Asignado"
    )
    
    # --- Datos del Producto ---
    tipo_producto = models.CharField(
        max_length=3, 
        choices=TIPO_PRODUCTO, 
        default='PE',
        verbose_name="Tipo de Producto"
    )
    
    nombre = models.CharField(max_length=100, verbose_name="Nombre Comercial")
    descripcion = models.CharField(max_length=255, verbose_name="Descripción")
    
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio de Venta")
    
    tipo_presentacion = models.CharField(
        max_length=3, 
        choices=TIPO_PRESENTACION,
        verbose_name="Presentación"
    )
    
    # Stock inicia en 0. Se llenará luego con el módulo de Compras/Pedidos.
    stock = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        verbose_name="Stock Actual"
    )

    estado = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        # Validación de seguridad: si borraron el proveedor, muestra texto alternativo
        nombre_proveedor = self.proveedor.nombre_contacto if self.proveedor else "Sin Proveedor"
        return f"{self.nombre} ({nombre_proveedor})"