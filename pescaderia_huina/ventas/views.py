from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView
from django.contrib import messages
from django.db.models import Q, Sum
from django.db import transaction
from datetime import datetime

from .models import Venta, DetalleVenta, Producto
from .forms import VentaForm, DetalleVentaForm, DetalleVentaFormSet, BuscarVentaForm, CancelarVentaForm


class ListaVentasView(ListView):
    """
    Vista para listar todas las ventas con filtros de búsqueda (Historia #11, #19)
    """
    model = Venta
    template_name = 'lista_ventas.html'
    context_object_name = 'ventas'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Venta.objects.all().prefetch_related('detalles__producto')
        
        # Aplicar filtros de búsqueda
        form = BuscarVentaForm(self.request.GET)
        
        if form.is_valid():
            fecha_inicio = form.cleaned_data.get('fecha_inicio')
            fecha_fin = form.cleaned_data.get('fecha_fin')
            estado = form.cleaned_data.get('estado')
            buscar = form.cleaned_data.get('buscar')
            
            if fecha_inicio:
                queryset = queryset.filter(fecha_venta__date__gte=fecha_inicio)
            
            if fecha_fin:
                queryset = queryset.filter(fecha_venta__date__lte=fecha_fin)
            
            if estado:
                queryset = queryset.filter(estado=estado)
            
            if buscar:
                queryset = queryset.filter(
                    Q(id__icontains=buscar) |
                    Q(observaciones__icontains=buscar)
                )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_busqueda'] = BuscarVentaForm(self.request.GET)
        
        # Agregar estadísticas
        ventas = self.get_queryset()
        context['total_ventas'] = ventas.filter(estado='COMPLETADA').count()
        context['total_ingresos'] = ventas.filter(estado='COMPLETADA').aggregate(
            total=Sum('total')
        )['total'] or 0
        
        return context


# ========== DETALLE DE VENTA (Historia #11) ==========
class DetalleVentaView(DetailView):
    """
    Vista para ver el detalle completo de una venta (Historia #11)
    Muestra productos, cantidades, precios y estado
    """
    model = Venta
    template_name = 'detalle_venta.html'
    context_object_name = 'venta'
    pk_url_kwarg = 'venta_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['detalles'] = self.object.detalles.select_related('producto').all()
        return context


# ========== CREAR VENTA (Historia #10) ==========
class CrearVentaView(CreateView):
    """
    Vista para registrar una nueva venta al detalle (Historia #10)
    Permite asociar productos y cantidades, procesando la transacción
    y descontando del inventario
    """
    model = Venta
    form_class = VentaForm
    template_name = 'crear_venta.html'
    success_url = reverse_lazy('ventas:lista_ventas')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = DetalleVentaFormSet(self.request.POST)
        else:
            context['formset'] = DetalleVentaFormSet()
        
        # Agregar lista de productos disponibles para JavaScript
        context['productos'] = Producto.objects.filter(
            activo=True,
            cantidad_disponible__gt=0
        ).values('id', 'nombre', 'precio_base', 'cantidad_disponible', 'unidad_medida')
        
        return context
    
    def form_valid(self, form):
        """
        Procesar la venta y descontar del inventario (Historia #10)
        """
        context = self.get_context_data()
        formset = context['formset']
        
        # Validar el formset
        if not formset.is_valid():
            messages.error(
                self.request,
                'Por favor, corrija los errores en los productos.'
            )
            return self.form_invalid(form)
        
        # Usar transacción para garantizar consistencia de datos
        with transaction.atomic():
            # Guardar la venta
            self.object = form.save(commit=False)
            self.object.estado = 'COMPLETADA'
            self.object.save()
            
            # Guardar los detalles y actualizar el inventario
            total = 0
            for detalle_form in formset:
                if detalle_form.cleaned_data and not detalle_form.cleaned_data.get('DELETE'):
                    detalle = detalle_form.save(commit=False)
                    detalle.venta = self.object
                    
                    # Descontar del inventario
                    producto = detalle.producto
                    if producto.cantidad_disponible >= detalle.cantidad:
                        producto.cantidad_disponible -= detalle.cantidad
                        producto.save()
                        
                        detalle.save()
                        total += detalle.subtotal
                    else:
                        messages.error(
                            self.request,
                            f'Stock insuficiente para {producto.nombre}'
                        )
                        raise ValueError("Stock insuficiente")
            
            # Actualizar el total de la venta
            self.object.total = total
            self.object.save()
        
        messages.success(
            self.request,
            f'Venta #{self.object.id} registrada exitosamente por un total de ${self.object.total:,.2f}'
        )
        return redirect(self.success_url)
    
    def form_invalid(self, form):
        """Mostrar mensaje de error si el formulario es inválido (Historia #17)"""
        messages.error(
            self.request,
            'Por favor, corrija los errores en el formulario.'
        )
        return super().form_invalid(form)


# ========== CANCELAR VENTA (Historia #12) ==========
def cancelar_venta(request, venta_id):
    """
    Vista para cancelar o corregir una venta registrada (Historia #12)
    Revierte el stock al inventario
    """
    venta = get_object_or_404(Venta, id=venta_id)
    
    if venta.estado == 'CANCELADA':
        messages.warning(request, 'Esta venta ya ha sido cancelada.')
        return redirect('ventas:detalle_venta', venta_id=venta_id)
    
    if request.method == 'POST':
        form = CancelarVentaForm(request.POST)
        
        if form.is_valid():
            motivo = form.cleaned_data['motivo']
            
            # Usar transacción para garantizar consistencia
            with transaction.atomic():
                # Revertir el stock
                for detalle in venta.detalles.all():
                    producto = detalle.producto
                    producto.cantidad_disponible += detalle.cantidad
                    producto.save()
                
                # Actualizar la venta
                venta.estado = 'CANCELADA'
                venta.observaciones = f"CANCELADA: {motivo}\n\n{venta.observaciones or ''}"
                venta.save()
            
            messages.success(
                request,
                f'La venta #{venta.id} ha sido cancelada exitosamente. El stock ha sido revertido.'
            )
            return redirect('ventas:lista_ventas')
    else:
        form = CancelarVentaForm()
    
    context = {
        'venta': venta,
        'form': form,
    }
    return render(request, 'cancelar_venta.html', context)


# ========== EDITAR VENTA (Funcionalidad adicional) ==========
class EditarVentaView(UpdateView):
    """
    Vista para editar una venta existente (solo si no está cancelada)
    """
    model = Venta
    form_class = VentaForm
    template_name = 'editar_venta.html'
    pk_url_kwarg = 'venta_id'
    
    def get_success_url(self):
        return reverse_lazy('ventas:detalle_venta', kwargs={'venta_id': self.object.id})
    
    def dispatch(self, request, *args, **kwargs):
        """Verificar que la venta no esté cancelada"""
        venta = self.get_object()
        if venta.estado == 'CANCELADA':
            messages.error(request, 'No se puede editar una venta cancelada.')
            return redirect('ventas:detalle_venta', venta_id=venta.id)
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = DetalleVentaFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = DetalleVentaFormSet(instance=self.object)
        
        context['productos'] = Producto.objects.filter(
            activo=True
        ).values('id', 'nombre', 'precio_base', 'cantidad_disponible', 'unidad_medida')
        
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        if not formset.is_valid():
            messages.error(self.request, 'Por favor, corrija los errores en los productos.')
            return self.form_invalid(form)
        
        with transaction.atomic():
            self.object = form.save()
            
            # Revertir cambios anteriores en el inventario
            for detalle in self.object.detalles.all():
                producto = detalle.producto
                producto.cantidad_disponible += detalle.cantidad
                producto.save()
            
            # Eliminar detalles antiguos
            self.object.detalles.all().delete()
            
            # Guardar nuevos detalles
            total = 0
            for detalle_form in formset:
                if detalle_form.cleaned_data and not detalle_form.cleaned_data.get('DELETE'):
                    detalle = detalle_form.save(commit=False)
                    detalle.venta = self.object
                    
                    # Descontar del inventario
                    producto = detalle.producto
                    if producto.cantidad_disponible >= detalle.cantidad:
                        producto.cantidad_disponible -= detalle.cantidad
                        producto.save()
                        
                        detalle.save()
                        total += detalle.subtotal
                    else:
                        messages.error(self.request, f'Stock insuficiente para {producto.nombre}')
                        raise ValueError("Stock insuficiente")
            
            self.object.total = total
            self.object.save()
        
        messages.success(self.request, f'Venta #{self.object.id} actualizada exitosamente.')
        return redirect(self.get_success_url())
