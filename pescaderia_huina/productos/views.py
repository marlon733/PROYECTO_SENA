from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models.deletion import ProtectedError
from django.forms import modelformset_factory
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from .models import Producto
from .forms import ProductoForm, ProveedorSelectForm, ProductoItemForm

# 1. LISTA DE PRODUCTOS
@login_required
def productos_list(request):
    query = request.GET.get('q')
    presentacion = request.GET.get('presentacion')
    
    # .select_related('proveedor') optimiza la consulta para traer el nombre del proveedor de una vez
    productos = Producto.objects.select_related('proveedor').all().order_by('-id')

    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) |
            Q(proveedor__nombre_contacto__icontains=query) # También busca por nombre del proveedor
        )

    if presentacion:
        productos = productos.filter(tipo_presentacion=presentacion)

    # OPTIMIZACIÓN: Paginación para no cargar todos los productos
    paginator = Paginator(productos, 25)
    page = request.GET.get('page', 1)
    try:
        productos = paginator.page(page)
    except PageNotAnInteger:
        productos = paginator.page(1)
    except EmptyPage:
        productos = paginator.page(paginator.num_pages)

    context = {
        'productos': productos,
        'tipos_presentacion': Producto.TIPO_PRESENTACION,
    }

    return render(request, "producto_list.html", context)

# 2. DETALLE DE PRODUCTO
@login_required
def producto_detalle(request, id):
    producto = get_object_or_404(Producto, id=id)
    return render(request, "productos/producto_detalle.html", {"producto": producto})

# 3. CREAR PRODUCTO (LÓGICA MASIVA / FORMSET)
@login_required
def producto_crear(request):
    # Configuramos el FormSet: Usamos ProductoItemForm para las filas
    ProductoFormSet = modelformset_factory(
        Producto, 
        form=ProductoItemForm, 
        extra=1, # Empieza con 1 fila vacía
        can_delete=True
    )

    if request.method == "POST":
        # Cargamos el formulario del proveedor y el set de productos
        proveedor_form = ProveedorSelectForm(request.POST)
        formset = ProductoFormSet(request.POST, queryset=Producto.objects.none())

        if proveedor_form.is_valid() and formset.is_valid():
            # 1. Obtenemos el proveedor seleccionado
            proveedor = proveedor_form.cleaned_data['proveedor']
            
            # 2. Preparamos los productos sin guardar en BD aún
            nuevos_productos = formset.save(commit=False)
            
            # 3. A cada producto le asignamos el proveedor y guardamos
            for producto in nuevos_productos:
                if producto.nombre.strip():  # Solo guardar si tiene nombre
                    producto.proveedor = proveedor
                    producto.save()
            
            # Mensaje de éxito
            from django.contrib import messages
            cantidad_guardada = len([p for p in nuevos_productos if p.nombre.strip()])
            messages.success(request, f'✓ {cantidad_guardada} producto(s) guardado(s) exitosamente.')
            
            return redirect("productos:productos_list")
        else:
            # Mostrar errores
            from django.contrib import messages
            if not proveedor_form.is_valid():
                proveedor_error = proveedor_form.errors.get('proveedor', ['Este campo es obligatorio.'])[0]
                messages.error(request, f'Proveedor: {proveedor_error}')
            if not formset.is_valid():
                # Errores del formset
                errores_msg = []
                for i, form_errors in enumerate(formset.errors):
                    if form_errors:
                        detalles_fila = []
                        for campo, errores_campo in form_errors.items():
                            if errores_campo:
                                detalles_fila.append(f"{campo}: {errores_campo[0]}")
                        if detalles_fila:
                            errores_msg.append(f"Fila {i+1}: {', '.join(detalles_fila)}")
                if errores_msg:
                    messages.error(request, f'Errores en productos: {" | ".join(errores_msg)}')
    else:
        # GET: Formularios vacíos
        proveedor_form = ProveedorSelectForm()
        # queryset=none() asegura que no cargue productos viejos en la tabla de crear
        formset = ProductoFormSet(queryset=Producto.objects.none())

    return render(request, "producto_crear.html", {
        "proveedor_form": proveedor_form,
        "formset": formset
    })

# 4. EDITAR PRODUCTO (INDIVIDUAL)
@login_required
def producto_editar(request, id):
    producto = get_object_or_404(Producto, id=id)

    if request.method == "POST":
        # Usamos el ProductoForm completo (que incluye el selector de proveedor individual)
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            producto_actualizado = form.save()
            messages.success(request, f'Cambios guardados para "{producto_actualizado.nombre}".')
            return redirect("productos:productos_list")
        messages.error(request, 'No se pudo guardar. Revisa los campos marcados.')
    else:
        form = ProductoForm(instance=producto)

    # Pasamos 'producto' al contexto para poder poner el nombre en el título del HTML
    return render(request, "producto_editar.html", {"form": form, "producto": producto})

# 5. ELIMINAR PRODUCTO
@login_required
def producto_eliminar(request, id):
    producto = get_object_or_404(Producto, id=id)
    tiene_ventas = producto.ventas.exists() or producto.ventaitem_set.exists()
    tiene_pedidos = producto.detallepedido_set.exists()
    tiene_relaciones = tiene_ventas or tiene_pedidos
    
    if request.method == "POST":
        if tiene_relaciones:
            messages.error(
                request,
                "No se puede eliminar este producto porque ya está asociado a ventas o pedidos."
            )
            return redirect("productos:productos_list")

        try:
            producto.delete()
        except ProtectedError:
            messages.error(
                request,
                "No se puede eliminar este producto porque tiene registros relacionados."
            )
        return redirect("productos:productos_list")
        
    return render(
        request,
        "producto_eliminar.html",
        {
            "producto": producto,
            "tiene_relaciones": tiene_relaciones,
            "tiene_ventas": tiene_ventas,
            "tiene_pedidos": tiene_pedidos,
        },
    )