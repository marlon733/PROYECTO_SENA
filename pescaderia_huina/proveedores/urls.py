from django.urls import path
from . import views

app_name = "proveedores"

urlpatterns = [
    path('agregar/', views.agregar_proveedor, name='agregar_proveedor'),
]