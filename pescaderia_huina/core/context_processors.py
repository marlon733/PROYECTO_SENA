from decimal import Decimal

from django.db.models import DecimalField, ExpressionWrapper, F, Q, Sum, Value
from django.db.models.functions import Coalesce

from productos.models import Producto


LOW_STOCK_THRESHOLD = Decimal('10')


def _unidad_stock(tipo_presentacion):
    return 'Libras' if tipo_presentacion == 'LIB' else 'Unidades'


def low_stock_notifications(request):
    """Context processor para notificaciones de stock bajo o agotado."""
    productos = Producto.objects.filter(estado=True).annotate(
        recibido=Coalesce(
            Sum('detallepedido__cantidad', filter=Q(detallepedido__pedido__estado='REC')),
            Value(0),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        ),
        vendido=Coalesce(
            Sum('ventaitem__cantidad', filter=Q(ventaitem__venta__estado='COMPLETADA')),
            Value(0),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        ),
    ).annotate(
        stock_calc=ExpressionWrapper(
            F('recibido') - F('vendido'),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        )
    ).select_related('proveedor').order_by('nombre')

    low_stock_critical = []
    low_stock_warning = []

    for producto in productos:
        stock_actual = producto.stock_calc or Decimal('0')
        producto.stock_notif = int(round(float(stock_actual)))
        producto.unidad_stock = _unidad_stock(producto.tipo_presentacion)

        if stock_actual <= 0:
            low_stock_critical.append(producto)
        elif stock_actual <= LOW_STOCK_THRESHOLD:
            low_stock_warning.append(producto)

    return {
        'low_stock_critical': low_stock_critical,
        'low_stock_warning': low_stock_warning,
        'low_stock_count': len(low_stock_critical) + len(low_stock_warning),
        'low_stock_threshold': int(LOW_STOCK_THRESHOLD),
        'low_stock_products': low_stock_critical + low_stock_warning,
    }