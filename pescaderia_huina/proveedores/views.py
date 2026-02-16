from django.shortcuts import render, redirect, get_object_or_404
from .models import Proveedor
from .forms import ProveedorForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

# 1. LISTA DE PROVEEDORES (Tu Hub Principal)
@login_required()
def lista_proveedores(request):
    # Traemos todos los proveedores ordenados por nombre
    proveedores = Proveedor.objects.all().order_by('nombre_contacto')
    return render(request, 'lista_proveedores.html', {'proveedores': proveedores})

# 2. AGREGAR PROVEEDOR
@login_required
def agregar_proveedor(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('proveedores:lista_proveedores')
    else:
        form = ProveedorForm()
    return render(request, 'agregar_proveedores.html', {'form': form})

# 3. DETALLE DEL PROVEEDOR (Solo lectura)
def detalle_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, id=id)
    return render(request, 'detalle_proveedores.html', {'proveedor': proveedor})

# 4. MODIFICAR PROVEEDOR
@login_required
def modificar_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, id=id)
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            return redirect('proveedores:lista_proveedores')
    else:
        form = ProveedorForm(instance=proveedor)
    # Importante: enviamos el objeto proveedor también por si el template lo necesita
    return render(request, 'modificar_proveedores.html', {'form': form, 'proveedor': proveedor})

# 5. ELIMINAR PROVEEDOR
@login_required
def eliminar_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, id=id)
    if request.method == 'POST':
        proveedor.delete()
        return redirect('proveedores:lista_proveedores')
    return render(request, 'eliminar_proveedores.html', {'proveedor': proveedor})