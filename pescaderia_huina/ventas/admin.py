from django.contrib import admin
from .models import Venta

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre_cliente', 'documento_cliente', 'producto', 'cantidad', 'total', 'estado', 'fecha_venta']
    list_filter = ['estado', 'fecha_venta']
    search_fields = ['nombre_cliente', 'documento_cliente', 'producto__nombre']
    readonly_fields = ['fecha_venta', 'fecha_modificacion', 'total']
    
    fieldsets = (
        ('Información del Cliente', {
            'fields': ('nombre_cliente', 'documento_cliente')
        }),
        ('Detalles de la Venta', {
            'fields': ('producto', 'cantidad', 'precio_unitario', 'total')
        }),
        ('Estado y Observaciones', {
            'fields': ('estado', 'observaciones', 'fecha_venta', 'fecha_modificacion')
        }),
        ('Cancelación', {
            'fields': ('motivo_cancelacion', 'fecha_cancelacion'),
            'classes': ('collapse',)
        }),
    )