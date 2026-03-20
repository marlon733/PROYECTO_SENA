from django.urls import path
from . import views

app_name = 'copia_seguridad'

urlpatterns = [
    path('', views.lista_copias_seguridad, name='lista'),
    path('crear/', views.crear_copia_seguridad, name='crear'),
    path('restaurar/<int:copia_id>/', views.restaurar_copia_seguridad, name='restaurar'),
    path('eliminar/<int:copia_id>/', views.eliminar_copia_seguridad, name='eliminar'),
]
