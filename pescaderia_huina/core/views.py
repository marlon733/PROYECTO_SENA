from django.shortcuts import render
from django.http import HttpResponse, FileResponse
from django.template import loader
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import os
from django.conf import settings

def index(request):
    return render(request, 'core/index.html')


def restablecer(request):
  template = loader.get_template('core/restablecer.html')
  return HttpResponse(template.render())

def page_not_found_404(request, exception=None):
    """
    Vista para manejar errores 404 personalizados
    """
    return render(request, '404.html', status=404)

@login_required
def PanelAdmin_base(request):
    return render(request, 'core/panel_admin_base.html')
from productos.models import Producto

from .forms import BusquedaProductoForm

@login_required
def pagina_inventario(request):
    # procesar formulario de búsqueda/filtrado
    form = BusquedaProductoForm(request.GET or None)

    # OPTIMIZACIÓN: select_related para traer proveedor en una sola query
    productos = Producto.objects.select_related('proveedor')
    if form.is_valid():
        buscar = form.cleaned_data.get('buscar')
        tipo = form.cleaned_data.get('tipo_producto')
        if buscar:
            productos = productos.filter(nombre__icontains=buscar)
        if tipo:
            productos = productos.filter(tipo_producto=tipo)

    # OPTIMIZACIÓN: Paginación para cada categoría
    paginator = Paginator(productos, 50)
    page = request.GET.get('page', 1)
    try:
        productos_page = paginator.page(page)
    except PageNotAnInteger:
        productos_page = paginator.page(1)
    except EmptyPage:
        productos_page = paginator.page(paginator.num_pages)

    # Filtrar por categorías desde la página paginada
    pescados = [p for p in productos_page if p.tipo_producto == 'PE']
    mariscos = [p for p in productos_page if p.tipo_producto == 'MA']
    pollos = [p for p in productos_page if p.tipo_producto == 'PO']

    context = {
        'pescados': pescados,
        'mariscos': mariscos,
        'pollos': pollos,
        'form_busqueda': form,
        'productos': productos_page,
    }

    return render(request, 'core/inventario.html', context)

@login_required
def dashboard_view(request):
    """
    Vista principal del panel de administración
    """
    # Estadísticas generales
    now = timezone.now()
    total_usuarios = User.objects.count()
    usuarios_activos = User.objects.filter(is_active=True).count()
    total_administradores = User.objects.filter(is_staff=True).count()
    nuevos_usuarios_mes = User.objects.filter(
        date_joined__year=now.year,
        date_joined__month=now.month,
    ).count()
    
    # Últimos usuarios registrados
    ultimos_usuarios = User.objects.select_related('perfil').order_by('-date_joined')[:5]
    
    context = {
        'titulo': 'Panel de Administración',
        'total_usuarios': total_usuarios,
        'usuarios_activos': usuarios_activos,
        'total_administradores': total_administradores,
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

@login_required
def descargar_manual_usuario(request):
    """
    Vista para descargar el manual de usuario en PDF
    """
    # Ruta del archivo PDF
    pdf_path = os.path.join(settings.BASE_DIR, 'static', 'docs', 'Manual De Usuario Pescaderia Huina.pdf')
    
    # Verificar que el archivo existe
    if not os.path.exists(pdf_path):
        return HttpResponse('El archivo no fue encontrado', status=404)
    
    # Servir el archivo como descarga
    response = FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Manual De Usuario Pescaderia Huina.pdf"'
    return response