from django.urls import path
from . import views

app_name = 'proveedores'

urlpatterns = [
    path('', views.lista_proveedores, name='lista_proveedores'),
    path('nuevo/', views.agregar_proveedor, name='agregar_proveedores'),
    path('detalle/<int:id>/', views.detalle_proveedor, name='detalle_proveedores'),
    path('modificar/<int:id>/', views.modificar_proveedor, name='modificar_proveedores'),
    path('eliminar/<int:id>/', views.eliminar_proveedor, name='eliminar_proveedores'),
]