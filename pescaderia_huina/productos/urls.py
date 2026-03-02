from django.urls import path
from . import views 

# Importante: Esto permite usar {% url 'productos:...' %} en los HTML
app_name = 'productos'

urlpatterns = [
    
    # 1. Listado general y Búsqueda
    path("", views.productos_list, name="productos_list"),
    
    # 2. Creación (Ahora soporta carga masiva con la tabla)
    path("nuevo/", views.producto_crear, name="producto_crear"),
    
    # 3. Operaciones individuales por ID
    path("<int:id>/", views.producto_detalle, name="producto_detalle"),
    path("<int:id>/editar/", views.producto_editar, name="producto_editar"),
    path("<int:id>/eliminar/", views.producto_eliminar, name="producto_eliminar"),
    
]