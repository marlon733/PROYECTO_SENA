from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.models import User
def index(request):
    return render(request, 'core/index.html')

def login(request):
  template = loader.get_template('core/login.html')
  return HttpResponse(template.render())

def restablecer(request):
  template = loader.get_template('core/restablecer.html')
  return HttpResponse(template.render())

def PanelAdmin_base(request):
    return render(request, 'core/panel_admin_base.html')

def dashboard_view(request):
    """
    Vista principal del panel de administración
    """
    # Estadísticas generales
    total_usuarios = User.objects.count()
    usuarios_activos = User.objects.filter(is_active=True).count()
    usuarios_staff = User.objects.filter(is_staff=True).count()
    nuevos_usuarios_mes = User.objects.filter(
        date_joined__month=request.user.date_joined.month
    ).count()
    
    # Últimos usuarios registrados
    ultimos_usuarios = User.objects.select_related('perfil').order_by('-date_joined')[:5]
    
    context = {
        'titulo': 'Panel de Administración',
        'total_usuarios': total_usuarios,
        'usuarios_activos': usuarios_activos,
        'usuarios_staff': usuarios_staff,
        'nuevos_usuarios_mes': nuevos_usuarios_mes,
        'ultimos_usuarios': ultimos_usuarios,
    }
    return render(request, 'core/dashboard.html', context)