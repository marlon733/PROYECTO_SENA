from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    path('', views.lista_pedidos, name='lista_pedidos'),
    path('nuevo/', views.crear_pedido, name='crear_pedido'),
    path('editar/<int:id>/', views.editar_pedido, name='editar_pedido'),
    path('eliminar/<int:id>/', views.eliminar_pedido, name='eliminar_pedido'),
    path('detalle/<int:id>/', views.detalle_pedido, name='detalle_pedido'),
    path('cambiar-estado/<int:pedido_id>/', views.cambiar_estado_pedido, name='cambiar_estado_pedido'),
    
]