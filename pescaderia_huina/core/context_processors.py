from productos.models import Producto


def low_stock_notifications(request):
    """Context processor to add low-stock products info globally."""
    # Products with stock less than threshold
    threshold = 15
    low_stock = Producto.objects.filter(stock__lt=threshold).order_by('stock')
    return {
        'low_stock_products': low_stock,
        'low_stock_count': low_stock.count(),
        'low_stock_threshold': threshold,
    }