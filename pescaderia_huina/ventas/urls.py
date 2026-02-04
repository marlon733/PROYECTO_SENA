from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    path('', views.ListaVentasView.as_view(), name='lista_ventas'),
    path('crear/', views.CrearVentaView.as_view(), name='crear_venta'),
    path('<int:pk>/', views.DetalleVentaView.as_view(), name='detalle_venta'),
    path('<int:pk>/editar/', views.EditarVentaView.as_view(), name='editar_venta'),
    path('<int:pk>/cancelar/', views.CancelarVentaView.as_view(), name='cancelar_venta'),
]