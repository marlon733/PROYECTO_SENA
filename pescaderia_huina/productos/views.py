from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

@login_required
def productos_list(request):
    productos = Producto.objects.all()
    return render(request, "producto.html", {"productos": productos})

@login_required
def producto_detalle(request, id):
    producto = get_object_or_404(Producto, id=id)
    return render(request, "producto_detalle.html", {"producto": producto})

@login_required
def producto_crear(request):
    if request.method == "POST":
        Producto.objects.create(
            tipo_producto=request.POST.get("tipo_producto"),
            nombre=request.POST.get("nombre"),
            descripcion=request.POST.get("descripcion"),
            tipo_presentacion=request.POST.get("tipo_presentacion"),
            peso=request.POST.get("peso"),
            precio=request.POST.get("precio"),
            stock=request.POST.get("stock"),
            estado=True if request.POST.get("estado") else False
        )
        return redirect("productos:productos_list")

    return render(request, "producto_crear.html")


@login_required
def producto_editar(request, id):
    producto = get_object_or_404(Producto, id=id)

    if request.method == "POST":
        producto.nombre = request.POST.get("nombre")
        producto.tipo_producto = request.POST.get("tipo_producto")
        producto.descripcion = request.POST.get("descripcion")
        producto.precio = request.POST.get("precio")
        producto.tipo_presentacion = request.POST.get("tipo_presentacion")
        producto.peso = request.POST.get("peso")
        producto.stock = request.POST.get("stock")
        producto.estado = True if request.POST.get("estado") == "on" else False

        producto.save()
        return redirect("productos:productos_list")

    return render(request, "producto_editar.html", {
        "producto": producto
    })
@login_required
def producto_eliminar(request, id):
    producto = get_object_or_404(Producto, id=id)
    
    if request.method == "POST":
        producto.delete()
        return redirect("productos:productos_list")  
    return render(request, "producto_eliminar.html", {"producto": producto})