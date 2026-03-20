from decimal import Decimal

from productos.models import Producto


def low_stock_notifications(request):
    """Context processor para notificaciones de stock.
    
    Nota: El modelo Producto no tiene atributo 'stock',
    por lo que este processor devuelve listas vacías.
    """
    
    return {
        'low_stock_critical': [],
        'low_stock_warning': [],
        'low_stock_count': 0,
        'low_stock_threshold': 10,
        'low_stock_products': [],
    }