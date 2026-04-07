"""
Context Processor para Breadcrumbs
Genera automáticamente las migas de pan según la ruta actual
"""
from django.urls import reverse, NoReverseMatch


def get_breadcrumb_items(request):
    """
    Context processor que genera automáticamente los breadcrumbs
    según la URL actual del usuario.
    
    Estructura:
    - Panel de control (siempre presente)
    - Módulo (pedidos, productos, ventas, proveedores, inventario)
    - Página (lista, crear, editar, detalle)
    """
    
    path = request.path
    breadcrumb_items = []
    
    # Siempre incluir Panel de control
    try:
        dashboard_url = reverse('core:dashboard')
    except NoReverseMatch:
        dashboard_url = '/dashboard/'
    
    breadcrumb_items.append({
        'label': 'Panel de control',
        'url': dashboard_url,
        'active': path == '/dashboard/',
    })
    
    # Mapeo de patrones de URL a breadcrumbs
    breadcrumb_map = {
        # PEDIDOS
        'pedidos:lista_pedidos': {
            'breadcrumb_path': [
                {'label': 'Pedidos', 'url': None}
            ]
        },
        'pedidos:crear_pedido': {
            'breadcrumb_path': [
                {'label': 'Pedidos', 'url': 'pedidos:lista_pedidos'},
                {'label': 'Nuevo Pedido', 'url': None}
            ]
        },
        'pedidos:editar_pedido': {
            'breadcrumb_path': [
                {'label': 'Pedidos', 'url': 'pedidos:lista_pedidos'},
                {'label': 'Editar', 'url': None}
            ]
        },
        'pedidos:detalle_pedido': {
            'breadcrumb_path': [
                {'label': 'Pedidos', 'url': 'pedidos:lista_pedidos'},
                {'label': 'Detalle', 'url': None}
            ]
        },
        'pedidos:eliminar_pedido': {
            'breadcrumb_path': [
                {'label': 'Pedidos', 'url': 'pedidos:lista_pedidos'},
                {'label': 'Eliminar', 'url': None}
            ]
        },
        'pedidos:inventario_pedidos': {
            'breadcrumb_path': [
                {'label': 'Pedidos', 'url': 'pedidos:lista_pedidos'},
                {'label': 'Inventario', 'url': None}
            ]
        },
        
        # PRODUCTOS
        'productos:productos_list': {
            'breadcrumb_path': [
                {'label': 'Productos', 'url': None}
            ]
        },
        'productos:producto_crear': {
            'breadcrumb_path': [
                {'label': 'Productos', 'url': 'productos:productos_list'},
                {'label': 'Nuevo Producto', 'url': None}
            ]
        },
        'productos:producto_editar': {
            'breadcrumb_path': [
                {'label': 'Productos', 'url': 'productos:productos_list'},
                {'label': 'Editar', 'url': None}
            ]
        },
        'productos:producto_eliminar': {
            'breadcrumb_path': [
                {'label': 'Productos', 'url': 'productos:productos_list'},
                {'label': 'Eliminar', 'url': None}
            ]
        },
        'productos:producto_detalle': {
            'breadcrumb_path': [
                {'label': 'Productos', 'url': 'productos:productos_list'},
                {'label': 'Detalle', 'url': None}
            ]
        },
        
        # VENTAS
        'ventas:lista_ventas': {
            'breadcrumb_path': [
                {'label': 'Ventas', 'url': None}
            ]
        },
        'ventas:crear_venta': {
            'breadcrumb_path': [
                {'label': 'Ventas', 'url': 'ventas:lista_ventas'},
                {'label': 'Nueva Venta', 'url': None}
            ]
        },
        'ventas:editar_venta': {
            'breadcrumb_path': [
                {'label': 'Ventas', 'url': 'ventas:lista_ventas'},
                {'label': 'Editar', 'url': None}
            ]
        },
        'ventas:detalle_venta': {
            'breadcrumb_path': [
                {'label': 'Ventas', 'url': 'ventas:lista_ventas'},
                {'label': 'Detalle', 'url': None}
            ]
        },
        'ventas:cancelar_venta': {
            'breadcrumb_path': [
                {'label': 'Ventas', 'url': 'ventas:lista_ventas'},
                {'label': 'Cancelar', 'url': None}
            ]
        },
        
        # PROVEEDORES
        'proveedores:lista_proveedores': {
            'breadcrumb_path': [
                {'label': 'Proveedores', 'url': None}
            ]
        },
        'proveedores:agregar_proveedores': {
            'breadcrumb_path': [
                {'label': 'Proveedores', 'url': 'proveedores:lista_proveedores'},
                {'label': 'Nuevo', 'url': None}
            ]
        },
        'proveedores:modificar_proveedores': {
            'breadcrumb_path': [
                {'label': 'Proveedores', 'url': 'proveedores:lista_proveedores'},
                {'label': 'Editar', 'url': None}
            ]
        },
        'proveedores:detalle_proveedores': {
            'breadcrumb_path': [
                {'label': 'Proveedores', 'url': 'proveedores:lista_proveedores'},
                {'label': 'Detalle', 'url': None}
            ]
        },
        'proveedores:eliminar_proveedores': {
            'breadcrumb_path': [
                {'label': 'Proveedores', 'url': 'proveedores:lista_proveedores'},
                {'label': 'Eliminar', 'url': None}
            ]
        },
    }
    
    # Detectar la vista actual basada en resolver_match
    if request.resolver_match:
        namespace = request.resolver_match.namespace or ''
        url_name = request.resolver_match.url_name
        
        if namespace and url_name:
            full_name = f"{namespace}:{url_name}"
        else:
            full_name = url_name
        
        # Buscar en el mapa de breadcrumbs
        if full_name in breadcrumb_map:
            breadcrumb_path = breadcrumb_map[full_name].get('breadcrumb_path', [])
            
            for item in breadcrumb_path:
                is_last = item == breadcrumb_path[-1]
                
                # Resolver URL si es un nombre de ruta
                item_url = None
                if item['url'] and not is_last:
                    try:
                        item_url = reverse(item['url'])
                    except NoReverseMatch:
                        item_url = '#'
                
                breadcrumb_items.append({
                    'label': item['label'],
                    'url': item_url,
                    'active': is_last,
                })
            
            return {'breadcrumb_items': breadcrumb_items}
    
    # Fallback: crear breadcrumb genérico basado en el path
    path_parts = [p for p in path.split('/') if p]
    
    if path_parts:
        module_map = {
            'pedidos': {'label': 'Pedidos', 'icon': 'bi-cart'},
            'productos': {'label': 'Productos', 'icon': 'bi-box'},
            'ventas': {'label': 'Ventas', 'icon': 'bi-cash-coin'},
            'proveedores': {'label': 'Proveedores', 'icon': 'bi-person-lines-fill'},
            'inventario': {'label': 'Inventario', 'icon': 'bi-collection'},
        }
        
        module = path_parts[0]
        if module in module_map:
            breadcrumb_items.append({
                'label': module_map[module]['label'],
                'url': None,
                'active': len(path_parts) == 1,
                'icon': module_map[module]['icon'],
            })
            
            # Agregar subpáginas si existen
            if len(path_parts) > 1:
                action_map = {
                    'nuevo': 'Nuevo',
                    'crear': 'Crear',
                    'editar': 'Editar',
                    'eliminar': 'Eliminar',
                    'detalle': 'Detalle',
                    'inventario': 'Inventario',
                }
                
                for part in path_parts[1:]:
                    label = action_map.get(part, part.capitalize())
                    breadcrumb_items.append({
                        'label': label,
                        'url': None,
                        'active': True,
                    })
    
    return {
        'breadcrumb_items': breadcrumb_items,
    }

