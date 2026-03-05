from productos.models import Producto

def low_stock_notifications(request):
    """Context processor para notificaciones"""
    
    return {
        'low_stock_products': [],
        'low_stock_count': 0,
        'low_stock_threshold': 0,
    }