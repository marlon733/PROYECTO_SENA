from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

def index(request):
    return render(request, 'core/index.html')


def restablecer(request):
  template = loader.get_template('core/restablecer.html')
  return HttpResponse(template.render())
@login_required
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

def pagina_pescados(request):
    return render(request, 'core/pescados.html')

def pagina_mariscos(request):
    return render(request, 'core/mariscos.html')

def pagina_pollos(request):
    return render(request, 'core/pollos.html')