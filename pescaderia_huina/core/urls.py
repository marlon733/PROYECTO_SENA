from django.urls import path
from . import views 

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('login/restablecer/', views.restablecer, name='restablecer'),
    path('panel_admin_base/', views.PanelAdmin_base, name='panel_admin_base'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    ]