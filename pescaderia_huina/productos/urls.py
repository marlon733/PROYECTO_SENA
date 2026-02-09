from django.urls import path
from . import views 

app_name = 'productos'


urlpatterns = [
    
    path("", views.productos_list, name="productos_list"),
    path("nuevo/", views.producto_crear, name="producto_crear"),
    path("<int:id>/", views.producto_detalle, name="producto_detalle"),
    path("<int:id>/editar/", views.producto_editar, name="producto_editar"),
    path("<int:id>/eliminar/", views.producto_eliminar, name="producto_eliminar"),
    
]