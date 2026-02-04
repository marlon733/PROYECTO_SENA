from django.urls import path
from . import views 

app_name = 'productos'

urlpatterns = [
    path('', views.index, name='index'),

    path('producto/', views.producto, name='producto'),
    ]