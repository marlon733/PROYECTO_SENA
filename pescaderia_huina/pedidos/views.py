from django.shortcuts import render, redirect, get_object_or_404
from .models import Pedido, Proveedor, Producto, DetallePedido
from .forms import PedidoForm, DetallePedidoForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

@login_required
def lista_pedidos(request):
    # Trae todos los pedidos de la base de datos db.sqlite3 
    pedidos = Pedido.objects.all().order_by('-fecha')
    return render(request, 'lista_pedidos.html', {'pedidos': pedidos})
@login_required
def crear_pedido(request):
    if request.method == 'POST':
        form_pedido = PedidoForm(request.POST)
        form_detalle = DetallePedidoForm(request.POST)
        
        if form_pedido.is_valid() and form_detalle.is_valid():
            nuevo_pedido = form_pedido.save(commit=False)
            
            # Cálculo del total
            cantidad = form_detalle.cleaned_data['cantidad']
            precio = form_detalle.cleaned_data['precio_unitario']
            nuevo_pedido.valor_total = cantidad * precio
            
            nuevo_pedido.save()
            
            detalle = form_detalle.save(commit=False)
            detalle.pedido = nuevo_pedido
            detalle.save()
            
            messages.success(request, f"Pedido #{nuevo_pedido.id} registrado con éxito.")
            return redirect('lista_pedidos')
    else:
        form_pedido = PedidoForm()
        form_detalle = DetallePedidoForm()

    return render(request, 'crear_pedido.html', {
        'form_pedido': form_pedido,
        'form_detalle': form_detalle,
        'proveedores': Proveedor.objects.all(),
        'productos': Producto.objects.all()
    })
@login_required
def editar_pedido(request, id):
    pedido = get_object_or_404(Pedido, id=id)
    # Obtenemos el primer detalle asociado al pedido
    detalle = get_object_or_404(DetallePedido, pedido=pedido)

    if request.method == 'POST':
        form_pedido = PedidoForm(request.POST, instance=pedido)
        form_detalle = DetallePedidoForm(request.POST, instance=detalle)

        if form_pedido.is_valid() and form_detalle.is_valid():
            # Actualizar el valor total basado en los nuevos cambios del detalle
            cantidad = form_detalle.cleaned_data['cantidad']
            precio = form_detalle.cleaned_data['precio_unitario']
            
            pedido_obj = form_pedido.save(commit=False)
            pedido_obj.valor_total = cantidad * precio
            pedido_obj.save()
            
            form_detalle.save()
            
            messages.info(request, f"Pedido #{pedido.id} actualizado correctamente.")
            return redirect('lista_pedidos')
    else:
        form_pedido = PedidoForm(instance=pedido)
        form_detalle = DetallePedidoForm(instance=detalle)

    return render(request, 'editar_pedido.html', {
        'form_pedido': form_pedido,
        'form_detalle': form_detalle,
        'pedido': pedido
    })
@login_required
def eliminar_pedido(request, id):
    pedido = get_object_or_404(Pedido, id=id)
    
    if request.method == 'POST':
        pedido.delete()
        messages.warning(request, f"El pedido #{id} ha sido eliminado permanentemente.")
        return redirect('lista_pedidos')
        
    return render(request, 'eliminar_pedido.html', {'pedido': pedido})