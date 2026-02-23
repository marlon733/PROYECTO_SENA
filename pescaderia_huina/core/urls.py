from django.urls import path
from . import views 

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/restablecer/', views.restablecer, name='restablecer'),
    path('panel_admin_base/', views.PanelAdmin_base, name='panel_admin_base'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('pescados/', views.pagina_pescados, name='pescados'),
    path('mariscos/', views.pagina_mariscos, name='mariscos'),
    path('pollos/', views.pagina_pollos, name='pollos'),
    ]