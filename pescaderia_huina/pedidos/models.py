from django.db import models

class Proveedor(models.Model):
    # Usamos el NIT como llave primaria (ID)
    nit = models.CharField(max_length=20, primary_key=True, verbose_name="NIT")
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Proveedor")
    telefono = models.CharField(max_length=15, blank=True, null=True)
    correo = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.nit})"

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"

class Producto(models.Model):
    # Nota: Si ya tienes este modelo en otra app, impórtalo en lugar de crearlo aquí
    nombre = models.CharField(max_length=100)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    # Pillow permite manejar la imagen del producto
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True) 

    def __str__(self):
        return self.nombre

class Pedido(models.Model):
    ESTADOS_CHOICES = [
        ('PEN', 'Pendiente'),
        ('REC', 'Recibido'),
        ('CAN', 'Cancelado'),
    ]

    # Relación con Proveedor usando su NIT
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, verbose_name="Proveedor (NIT)")
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    estado = models.CharField(max_length=3, choices=ESTADOS_CHOICES, default='PEN')
    valor_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Pedido #{self.id} - {self.proveedor.nombre}"

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, help_text="Precio de compra al proveedor")

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.producto.nombre} (x{self.cantidad})"
