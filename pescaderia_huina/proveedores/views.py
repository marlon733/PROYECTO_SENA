from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q 
from .models import Proveedor
from .forms import ProveedorForm

# 1. LISTA DE PROVEEDORES
@login_required
def lista_proveedores(request):
    # Filtramos solo los activos
    proveedores = Proveedor.objects.filter(estado=True).order_by('nombre_contacto')

    # Lógica de Búsqueda
    query = request.GET.get('q')
    if query:
        proveedores = proveedores.filter(
            Q(nombre_contacto__icontains=query) | 
            Q(nit__icontains=query)
        )

    # CORRECCIÓN AQUÍ: Quitamos 'proveedores/' de la ruta
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
    # CORRECCIÓN AQUÍ
    return render(request, 'agregar_proveedores.html', {'form': form})

# 3. DETALLE DEL PROVEEDOR
@login_required
def detalle_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, id=id)
    # CORRECCIÓN AQUÍ
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
    
    # CORRECCIÓN AQUÍ
    return render(request, 'modificar_proveedores.html', {'form': form, 'proveedor': proveedor})

# 5. ELIMINAR PROVEEDOR (SOFT DELETE)
@login_required
def eliminar_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, id=id)
    
    if request.method == 'POST':
        # Soft delete: Solo cambiamos el estado
        proveedor.estado = False 
        proveedor.save()
        return redirect('proveedores:lista_proveedores')
        
    # CORRECCIÓN AQUÍ
    return render(request, 'eliminar_proveedores.html', {'proveedor': proveedor})