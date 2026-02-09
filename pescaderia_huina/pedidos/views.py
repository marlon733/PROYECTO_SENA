from django.shortcuts import render, redirect, get_object_or_404
from .models import Pedido, Proveedor, Producto, DetallePedido
from .forms import PedidoForm, DetallePedidoForm
from django.contrib import messages

def lista_pedidos(request):
    # Trae todos los pedidos de la base de datos db.sqlite3 
    pedidos = Pedido.objects.all().order_by('-fecha')
    return render(request, 'lista_pedidos.html', {'pedidos': pedidos})

def crear_pedido(request):
    if request.method == 'POST':
        form_pedido = PedidoForm(request.POST)
        form_detalle = DetallePedidoForm(request.POST)
        
        if form_pedido.is_valid() and form_detalle.is_valid():
            # 1. Guardar el pedido (sin commit para calcular el total)
            nuevo_pedido = form_pedido.save(commit=False)
            
            # 2. Obtener datos del detalle para calcular el total
            cantidad = form_detalle.cleaned_data['cantidad']
            precio = form_detalle.cleaned_data['precio_unitario']
            nuevo_pedido.valor_total = cantidad * precio
            
            # 3. Guardar el pedido definitivamente
            nuevo_pedido.save()
            
            # 4. Guardar el detalle vinculándolo al pedido
            detalle = form_detalle.save(commit=False)
            detalle.pedido = nuevo_pedido
            detalle.save()
            
            messages.success(request, f"Pedido #{nuevo_pedido.id} registrado con éxito.")
            return redirect('lista_pedidos')
    else:
        form_pedido = PedidoForm()
        form_detalle = DetallePedidoForm()

    # Mantenemos la compatibilidad con tu HTML de proveedores y productos
    return render(request, 'crear_pedido.html', {
        'form_pedido': form_pedido,
        'form_detalle': form_detalle,
        'proveedores': Proveedor.objects.all(),
        'productos': Producto.objects.all()
    })
