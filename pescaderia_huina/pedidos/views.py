from django.shortcuts import render, redirect, get_object_or_404
from .models import Pedido, DetallePedido
from .forms import PedidoForm, DetallePedidoForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from productos.models import Producto
from proveedores.models import Proveedor

@login_required
def lista_pedidos(request):
    pedidos = Pedido.objects.all().order_by('-fecha')
    return render(request, 'lista_pedidos.html', {'pedidos': pedidos})

@login_required
def crear_pedido(request):
    if request.method == 'POST':
        form_pedido = PedidoForm(request.POST)
        form_detalle = DetallePedidoForm(request.POST)
        
        # Obtenemos el precio del POST manualmente si no está en el form_detalle
        precio_unitario = request.POST.get('precio_unitario') 
        
        if form_pedido.is_valid() and form_detalle.is_valid():
            try:
                nuevo_pedido = form_pedido.save(commit=False)
                
                # Lógica de cálculo
                cantidad = form_detalle.cleaned_data.get('cantidad', 0)
                # Convertimos a float para asegurar la operación matemática
                precio = float(precio_unitario) if precio_unitario else 0
                
                nuevo_pedido.valor_total = cantidad * precio
                nuevo_pedido.save() # Guardamos para obtener ID
                
                detalle = form_detalle.save(commit=False)
                detalle.pedido = nuevo_pedido
                detalle.save()
                
                messages.success(request, f"Pedido #{nuevo_pedido.id} registrado con éxito.")
                return redirect('pedidos:lista_pedidos') # Asegúrate del namespace
            except Exception as e:
                messages.error(request, f"Error al procesar el pedido: {e}")
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        form_pedido = PedidoForm()
        form_detalle = DetallePedidoForm()

    return render(request, 'crear_pedido.html', {
        'form_pedido': form_pedido,
        'form_detalle': form_detalle,
    })

@login_required
def editar_pedido(request, id):
    pedido = get_object_or_404(Pedido, id=id)
    detalle = get_object_or_404(DetallePedido, pedido=pedido)

    if request.method == 'POST':
        form_pedido = PedidoForm(request.POST, instance=pedido)
        form_detalle = DetallePedidoForm(request.POST, instance=detalle)
        precio_unitario = request.POST.get('precio_unitario')

        if form_pedido.is_valid() and form_detalle.is_valid():
            cantidad = form_detalle.cleaned_data.get('cantidad', 0)
            precio = float(precio_unitario) if precio_unitario else 0
            
            pedido_obj = form_pedido.save(commit=False)
            pedido_obj.valor_total = cantidad * precio
            pedido_obj.save()
            
            form_detalle.save()
            
            messages.info(request, f"Pedido #{pedido.id} actualizado correctamente.")
            return redirect('pedidos:lista_pedidos') # Cambiado para ser consistente
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
    # 1. Buscamos el pedido
    pedido = get_object_or_404(Pedido, id=id)
    
    # 2. Si el usuario confirma (clic en el botón del formulario de confirmación)
    if request.method == 'POST':
        pedido.delete()
        messages.warning(request, f"El pedido #{id} ha sido eliminado.")
        return redirect('pedidos:lista_pedidos') # Asegúrate de incluir el namespace
        
    # 3. Si entra por GET (al hacer clic en la tabla), muestra el HTML de confirmación
    return render(request, 'eliminar_pedido.html', {'pedido': pedido})