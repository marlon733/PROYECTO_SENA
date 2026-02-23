from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ProductoForm
from django.db.models import Q

@login_required
def productos_list(request):
    query = request.GET.get('q')
    productos = Producto.objects.all()

    if query:
        productos = productos.filter(
            Q(nombre__icontains=query)
        )

    context = {
        'productos': productos
    }

    return render(request, "producto_list.html", context)
@login_required
def producto_detalle(request, id):
    producto = get_object_or_404(Producto, id=id)
    return render(request, "productos/producto_detalle.html", {"producto": producto})

@login_required
def producto_crear(request):
    if request.method == "POST":
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("productos:productos_list")
    else:
        form = ProductoForm()

    return render(request, "producto_crear.html", {"form": form})


def producto_editar(request, id):
    producto = get_object_or_404(Producto, id=id)

    if request.method == "POST":
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect("productos:productos_list")
    else:
        form = ProductoForm(instance=producto)

    return render(request, "producto_editar.html", {"form": form})
@login_required
def producto_eliminar(request, id):
    producto = get_object_or_404(Producto, id=id)
    
    if request.method == "POST":
        producto.delete()
        return redirect("productos:productos_list")  
    return render(request, "producto_eliminar.html", {"producto": producto})