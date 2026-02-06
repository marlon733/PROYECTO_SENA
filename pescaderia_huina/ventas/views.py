from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader
from django.http import HttpResponse
from django.views import generic
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Sum
from django.db import transaction
from django.utils import timezone
from .models import Venta
from .forms import VentaForm, CancelarVentaForm, BusquedaVentaForm
from productos.models import Producto


@login_required
def ventas(request):
    """Vista para listar todas las ventas"""
    lista_ventas = Venta.objects.all()
    
    # Aplicar filtros si existen
    form_busqueda = BusquedaVentaForm(request.GET)
    if form_busqueda.is_valid():
        fecha_inicio = form_busqueda.cleaned_data.get('fecha_inicio')
        fecha_fin = form_busqueda.cleaned_data.get('fecha_fin')
        estado = form_busqueda.cleaned_data.get('estado')
        buscar = form_busqueda.cleaned_data.get('buscar')
        
        if fecha_inicio:
            lista_ventas = lista_ventas.filter(fecha_venta__gte=fecha_inicio)
        if fecha_fin:
            lista_ventas = lista_ventas.filter(fecha_venta__lte=fecha_fin)
        if estado:
            lista_ventas = lista_ventas.filter(estado=estado)
        if buscar:
            lista_ventas = lista_ventas.filter(
                Q(nombre_cliente__icontains=buscar) |
                Q(documento_cliente__icontains=buscar)
            )
    
    # Calcular estadísticas
    total_ventas = Venta.objects.filter(estado='COMPLETADA').count()
    total_ingresos = Venta.objects.filter(estado='COMPLETADA').aggregate(
        total=Sum('total')
    )['total'] or 0
    
    template = loader.get_template('lista_ventas.html')
    context = {
        'lista_ventas': lista_ventas,
        'form_busqueda': form_busqueda,
        'total_ventas': total_ventas,
        'total_ingresos': total_ingresos,
    }
    return HttpResponse(template.render(context, request))


@login_required
def detalle_venta(request, id_venta):
    """Vista para ver el detalle de una venta"""
    venta = Venta.objects.get(id=id_venta)
    template = loader.get_template('detalle_venta.html')
    context = {
        'venta': venta,
    }
    return HttpResponse(template.render(context, request))


# CREATE - VENTA
class VentaCreateView(LoginRequiredMixin, generic.CreateView):
    """Vista para crear una nueva venta"""
    model = Venta
    form_class = VentaForm
    template_name = 'crear_venta.html'
    success_url = reverse_lazy('ventas:lista_ventas')
    
    def form_valid(self, form):
        """Procesar la venta y actualizar el stock"""
        with transaction.atomic():
            # Guardar la venta
            venta = form.save(commit=False)
            venta.save()
            
            # Actualizar stock del producto
            producto = venta.producto
            producto.stock -= venta.cantidad
            producto.save()
            
            messages.success(
                self.request,
                f'La venta #{venta.id} para {venta.nombre_cliente} ha sido registrada exitosamente.'
            )
            return super().form_valid(form)
    
    def form_invalid(self, form):
        """Mostrar mensaje de error si el formulario es inválido"""
        messages.error(
            self.request,
            'Por favor, corrija los errores en el formulario.'
        )
        return super().form_invalid(form)


# UPDATE - VENTA
class VentaUpdateView(LoginRequiredMixin, generic.UpdateView):
    """Vista para actualizar una venta existente"""
    model = Venta
    form_class = VentaForm
    template_name = 'editar_venta.html'
    success_url = reverse_lazy('ventas:lista_ventas')
    pk_url_kwarg = 'venta_id'
    
    def dispatch(self, request, *args, **kwargs):
        """Verificar que la venta no esté cancelada"""
        venta = self.get_object()
        if venta.estado == 'CANCELADA':
            messages.warning(request, 'No se puede editar una venta cancelada')
            return redirect('ventas:detalle_venta', id_venta=venta.id)
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Procesar la actualización y ajustar el stock"""
        with transaction.atomic():
            venta_original = Venta.objects.get(pk=self.object.pk)
            
            # Revertir el stock original
            producto_original = venta_original.producto
            producto_original.stock += venta_original.cantidad
            producto_original.save()
            
            # Guardar la venta actualizada
            venta = form.save(commit=False)
            venta.save()
            
            # Aplicar el nuevo stock
            producto_nuevo = venta.producto
            producto_nuevo.stock -= venta.cantidad
            producto_nuevo.save()
            
            messages.success(
                self.request,
                f'La venta #{venta.id} ha sido actualizada exitosamente.'
            )
            return super().form_valid(form)
    
    def form_invalid(self, form):
        """Mostrar mensaje de error si el formulario es inválido"""
        messages.error(
            self.request,
            'Por favor, corrija los errores en el formulario.'
        )
        return super().form_invalid(form)


# CANCEL - VENTA (equivalente a DELETE)
class VentaCancelarView(LoginRequiredMixin, generic.FormView):
    """Vista para cancelar una venta"""
    template_name = 'cancelar_venta.html'
    form_class = CancelarVentaForm
    
    def dispatch(self, request, *args, **kwargs):
        """Obtener la venta y verificar si ya está cancelada"""
        self.venta = get_object_or_404(Venta, pk=kwargs['venta_id'])
        if self.venta.estado == 'CANCELADA':
            messages.warning(request, 'Esta venta ya está cancelada')
            return redirect('ventas:detalle_venta', id_venta=self.venta.id)
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['venta'] = self.venta
        return context
    
    def get_success_url(self):
        return reverse_lazy('ventas:detalle_venta', kwargs={'id_venta': self.venta.id})
    
    def form_valid(self, form):
        """Cancelar la venta y revertir el stock"""
        with transaction.atomic():
            # Revertir stock
            producto = self.venta.producto
            producto.stock += self.venta.cantidad
            producto.save()
            
            # Actualizar venta
            self.venta.estado = 'CANCELADA'
            self.venta.motivo_cancelacion = form.cleaned_data['motivo']
            self.venta.fecha_cancelacion = timezone.now()
            self.venta.save()
            
            messages.success(
                self.request,
                f'La venta #{self.venta.id} ha sido cancelada exitosamente.'
            )
            return super().form_valid(form)