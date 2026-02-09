from django.urls import path
from . import views 

app_name = 'ventas'

urlpatterns = [
    path('', views.ventas, name='lista_ventas'),
    path('venta/<int:id_venta>/', views.detalle_venta, name='detalle_venta'),
    path('crear/', views.VentaCreateView.as_view(), name='crear_venta'),
    path('<int:venta_id>/editar/', views.VentaUpdateView.as_view(), name='editar_venta'),
    path('<int:venta_id>/cancelar/', views.VentaCancelarView.as_view(), name='cancelar_venta'),
]