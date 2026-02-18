from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory
from django.db.models import Sum, Q, F

from .models import Pedido, DetallePedido
from .forms import PedidoForm, DetallePedidoForm

# Creamos la fábrica de formularios. Permite crear múltiples Detalles vinculados a 1 Pedido
DetallePedidoFormSet = inlineformset_factory(
    Pedido, 
    DetallePedido, 
    form=DetallePedidoForm, 
    extra=1, # Muestra 1 fila en blanco al cargar la página
    can_delete=True
)

@login_required
def lista_pedidos(request):
    pedidos = Pedido.objects.annotate(
        cantidad_total_calculada=Sum('detalles__cantidad') 
    ).order_by('-fecha')

    # Capturamos los parámetros de la URL
    query = request.GET.get('q')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    # 1. Filtro por texto (ID, Proveedor, NIT o Nombre del Producto)
    if query:
        pedidos = pedidos.filter(
            Q(id__icontains=query) | 
            Q(proveedor__nombre_contacto__icontains=query) | 
            Q(proveedor__nit__icontains=query) |
            Q(detalles__producto__nombre__icontains=query) # Busca en el nombre del producto
        ).distinct() # IMPORTANTE: distinct() evita que un pedido salga duplicado si tiene varios productos que coinciden

    # 2. Filtro por Rango de Fechas
    if fecha_inicio:
        pedidos = pedidos.filter(fecha__date__gte=fecha_inicio) # gte = Mayor o igual que
    if fecha_fin:
        pedidos = pedidos.filter(fecha__date__lte=fecha_fin)    # lte = Menor o igual que
        
    return render(request, 'lista_pedidos.html', {'pedidos': pedidos})

@login_required
def crear_pedido(request):
    if request.method == 'POST':
        form_pedido = PedidoForm(request.POST)
        formset = DetallePedidoFormSet(request.POST) # Recibe los N productos del template
        
        if form_pedido.is_valid() and formset.is_valid():
            try:
                # Guardamos el encabezado del pedido sin hacer commit
                nuevo_pedido = form_pedido.save(commit=False)
                nuevo_pedido.valor_total = 0 
                nuevo_pedido.save() # Se guarda en BD para obtener un ID
                
                total_general = 0
                detalles = formset.save(commit=False)
                
                # Iteramos sobre todos los productos agregados en la vista
                for detalle in detalles:
                    detalle.pedido = nuevo_pedido # Vinculamos al pedido padre
                    
                    # Asegúrate de que tu modelo DetallePedido tenga los campos cantidad y precio_unitario
                    subtotal = (detalle.cantidad or 0) * (detalle.precio_unitario or 0)
                    total_general += subtotal
                    detalle.save()
                
                # Actualizamos el total real sumando todos los productos
                nuevo_pedido.valor_total = total_general
                nuevo_pedido.save()
                
                messages.success(request, f"Pedido #{nuevo_pedido.id} registrado con éxito.")
                return redirect('pedidos:lista_pedidos')
            except Exception as e:
                messages.error(request, f"Ocurrió un error: {e}")
        else:
            messages.error(request, "Por favor corrige los errores del formulario.")
    else:
        form_pedido = PedidoForm()
        formset = DetallePedidoFormSet()

    return render(request, 'crear_pedido.html', {
        'form_pedido': form_pedido,
        'formset': formset, # Pasamos el formset en lugar de un solo form_detalle
    })

@login_required
def editar_pedido(request, id):
    pedido = get_object_or_404(Pedido, id=id)
    
    if request.method == 'POST':
        form_pedido = PedidoForm(request.POST, instance=pedido)
        formset = DetallePedidoFormSet(request.POST, instance=pedido)

        if form_pedido.is_valid() and formset.is_valid():
            pedido_obj = form_pedido.save(commit=False)
            
            # Guardamos los detalles (incluyendo eliminaciones)
            formset.save()
            
            # Recalculamos el valor total después de la edición
            # SOLUCIÓN: Usamos 'detalles' y multiplicamos cantidad por precio_unitario
            total_recalculado = Pedido.objects.filter(id=id).aggregate(
                total=Sum(F('detalles__cantidad') * F('detalles__precio_unitario'))
            )['total'] or 0
            
            pedido_obj.valor_total = total_recalculado
            pedido_obj.save()
            
            messages.info(request, f"Pedido #{pedido.id} actualizado correctamente.")
            return redirect('pedidos:lista_pedidos')
    else:
        form_pedido = PedidoForm(instance=pedido)
        formset = DetallePedidoFormSet(instance=pedido)

    return render(request, 'editar_pedido.html', {
        'form_pedido': form_pedido,
        'formset': formset,
        'pedido': pedido
    })

@login_required
def eliminar_pedido(request, id):
    pedido = get_object_or_404(Pedido, id=id)
    if request.method == 'POST':
        pedido.delete()
        messages.warning(request, f"El pedido #{id} ha sido eliminado.")
        return redirect('pedidos:lista_pedidos')
    return render(request, 'eliminar_pedido.html', {'pedido': pedido})