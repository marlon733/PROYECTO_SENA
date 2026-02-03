from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    path('', views.ListaVentasView.as_view(), name='lista_ventas'),
    
    path('<int:venta_id>/', views.DetalleVentaView.as_view(), name='detalle_venta'),
    
    path('crear/', views.CrearVentaView.as_view(), name='crear_venta'),
    
    path('<int:venta_id>/editar/', views.EditarVentaView.as_view(), name='editar_venta'),
    
    path('<int:venta_id>/cancelar/', views.cancelar_venta, name='cancelar_venta'),
]
