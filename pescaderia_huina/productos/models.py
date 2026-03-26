from django.db import models
from django.db.models import Sum, Q
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
        ('LIB', 'Libras'),
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
    descripcion = models.CharField(max_length=255, blank=True, default="", verbose_name="Descripción")
    
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio de Venta")
    
    tipo_presentacion = models.CharField(
        max_length=3, 
        choices=TIPO_PRESENTACION,
        verbose_name="Presentación"
    )
    
    # Stock inicia en 0. Se llenará luego con el módulo de Compras/Pedidos.


    estado = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    @property
    def cantidad_total_calculado(self):
        """
        Calcula la cantidad total de este producto en todos los pedidos pendientes.
        """
        from pedidos.models import DetallePedido, Pedido
        
        total = DetallePedido.objects.filter(
            producto=self,
            pedido__estado='PEN'  # Solo pedidos pendientes
        ).aggregate(total=Sum('cantidad'))['total']
        
        return total or 0

    def __str__(self):
        # Validación de seguridad: si borraron el proveedor, muestra texto alternativo
        nombre_proveedor = self.proveedor.nombre_contacto if self.proveedor else "Sin Proveedor"
        return f"{self.nombre} ({nombre_proveedor})"
    
    @property
    def stock(self):
        """
        Stock = cantidad recibida en pedidos (estado REC)
                − cantidad vendida en ventas COMPLETADA
        """
        from django.db.models import Sum
        from django.db import DatabaseError, InterfaceError

        try:
            # Total recibido en pedidos con estado REC
            recibido = self.detallepedido_set.filter(
                pedido__estado='REC'
            ).aggregate(total=Sum('cantidad'))['total'] or 0

            # Total vendido solo en ventas completadas
            vendido = self.ventaitem_set.filter(
                venta__estado='COMPLETADA'
            ).aggregate(total=Sum('cantidad'))['total'] or 0

            return recibido - vendido
        except (DatabaseError, InterfaceError):
            # Si la conexión está cerrada o hay error temporal de BD,
            # devolvemos 0 para no romper el render de páginas críticas.
            return 0