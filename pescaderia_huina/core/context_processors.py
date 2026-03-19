from decimal import Decimal

from productos.models import Producto


def low_stock_notifications(request):
    """Context processor para notificaciones de stock.
    
    Separa productos en dos categorías:
    - low_stock_critical: stock_disponible = 0 (rojo)
    - low_stock_warning: stock_disponible entre 1 y 10 (amarillo)
    """
    
    threshold = 10
    productos = Producto.objects.filter(estado=True)
    
    low_stock_critical = []  # stock = 0
    low_stock_warning = []   # stock entre 10 y 15
    
    for p in productos:
        stock_disponible = Decimal(str(p.stock))
        
        if stock_disponible <= 0:
            low_stock_critical.append({
                'nombre': p.nombre,
                'stock': stock_disponible,
            })
        elif 1 <= stock_disponible <= threshold:
            low_stock_warning.append({
                'nombre': p.nombre,
                'stock': stock_disponible,
            })
    
    total_alertas = len(low_stock_critical) + len(low_stock_warning)
    
    return {
        'low_stock_critical': low_stock_critical,
        'low_stock_warning': low_stock_warning,
        'low_stock_count': total_alertas,
        'low_stock_threshold': threshold,
        'low_stock_products': low_stock_critical + low_stock_warning,  # compatibilidad
    }