from django.contrib import admin
from .models import Producto, Venta, DetalleVenta


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'unidad_medida', 'precio_base', 'cantidad_disponible', 'activo']
    list_filter = ['activo', 'unidad_medida']
    search_fields = ['nombre']
    list_editable = ['activo']


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1
    readonly_fields = ['subtotal']


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ['id', 'fecha_venta', 'total', 'estado', 'cantidad_productos']
    list_filter = ['estado', 'fecha_venta']
    search_fields = ['id', 'observaciones']
    readonly_fields = ['fecha_venta', 'fecha_modificacion', 'total']
    inlines = [DetalleVentaInline]
    
    def cantidad_productos(self, obj):
        return obj.cantidad_productos()
    cantidad_productos.short_description = 'Productos'