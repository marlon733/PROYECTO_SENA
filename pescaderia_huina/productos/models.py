from django.db import models
# Importamos el modelo de la otra app para "traer los IDs"
from proveedores.models import Proveedor 

class Producto(models.Model):
    # --- Opciones de Selección ---
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

    # --- La Conexión Clave (Lo que pediste) ---
    # Esto crea un campo desplegable en tu formulario donde
    # seleccionas al proveedor por su nombre, pero guarda su ID internamente.
    proveedor = models.ForeignKey(
        Proveedor, 
        on_delete=models.CASCADE, # Si eliminas al proveedor, se borran sus productos
        related_name='productos', # Permite buscar "proveedor.productos.all"
        verbose_name="Seleccionar Proveedor"
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

    def _str_(self):
        return f"{self.nombre} - {self.proveedor.nombre_contacto}"