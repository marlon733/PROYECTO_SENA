from django.views.generic import ListView, CreateView, DetailView, UpdateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Sum
from django.db import transaction
from django.utils import timezone
from .models import Venta, DetalleVenta
from .forms import VentaForm, DetalleVentaFormSet, CancelarVentaForm, BusquedaVentaForm
from productos.models import Producto  # Ajustar según tu app
import json

class ListaVentasView(LoginRequiredMixin, ListView):
    model = Venta
    template_name = 'ventas/lista_ventas.html'
    context_object_name = 'ventas'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        form = BusquedaVentaForm(self.request.GET)
        
        if form.is_valid():
            fecha_inicio = form.cleaned_data.get('fecha_inicio')
            fecha_fin = form.cleaned_data.get('fecha_fin')
            estado = form.cleaned_data.get('estado')
            buscar = form.cleaned_data.get('buscar')
            
            if fecha_inicio:
                queryset = queryset.filter(fecha_venta__gte=fecha_inicio)
            if fecha_fin:
                queryset = queryset.filter(fecha_venta__lte=fecha_fin)
            if estado:
                queryset = queryset.filter(estado=estado)
            if buscar:
                queryset = queryset.filter(id__icontains=buscar)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_ventas'] = Venta.objects.filter(estado='COMPLETADA').count()
        context['total_ingresos'] = Venta.objects.filter(
            estado='COMPLETADA'
        ).aggregate(total=Sum('total'))['total'] or 0
        context['form_busqueda'] = BusquedaVentaForm(self.request.GET)
        return context


class CrearVentaView(LoginRequiredMixin, CreateView):
    model = Venta
    form_class = VentaForm
    template_name = 'ventas/crear_venta.html'
    success_url = reverse_lazy('ventas:lista_ventas')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = DetalleVentaFormSet(self.request.POST)
        else:
            context['formset'] = DetalleVentaFormSet()
        
        # Pasar productos como JSON para el JavaScript
        productos = Producto.objects.all().values(
            'id', 'nombre', 'precio_base', 'cantidad_disponible', 'unidad_medida'
        )
        context['productos'] = json.dumps(list(productos))
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        if formset.is_valid():
            with transaction.atomic():
                # Guardar la venta
                self.object = form.save(commit=False)
                total = 0
                
                # Guardar detalles y calcular total
                formset.instance = self.object
                detalles = formset.save(commit=False)
                
                for detalle in detalles:
                    # Validar stock
                    if detalle.cantidad > detalle.producto.cantidad_disponible:
                        messages.error(
                            self.request, 
                            f'No hay suficiente stock de {detalle.producto.nombre}'
                        )
                        return self.form_invalid(form)
                    
                    # Actualizar stock
                    detalle.producto.cantidad_disponible -= detalle.cantidad
                    detalle.producto.save()
                    
                    total += detalle.subtotal
                
                # Guardar venta con el total calculado
                self.object.total = total
                self.object.save()
                
                # Guardar detalles
                for detalle in detalles:
                    detalle.save()
                
                messages.success(self.request, 'Venta registrada exitosamente')
                return redirect(self.success_url)
        else:
            return self.form_invalid(form)


class DetalleVentaView(LoginRequiredMixin, DetailView):
    model = Venta
    template_name = 'ventas/detalle_venta.html'
    context_object_name = 'venta'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['detalles'] = self.object.detalles.all()
        return context


class EditarVentaView(LoginRequiredMixin, UpdateView):
    model = Venta
    form_class = VentaForm
    template_name = 'ventas/editar_venta.html'
    
    def get_success_url(self):
        return reverse('ventas:detalle_venta', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = DetalleVentaFormSet(
                self.request.POST, 
                instance=self.object
            )
        else:
            context['formset'] = DetalleVentaFormSet(instance=self.object)
        
        productos = Producto.objects.all().values(
            'id', 'nombre', 'precio_base', 'cantidad_disponible', 'unidad_medida'
        )
        context['productos'] = json.dumps(list(productos))
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        if formset.is_valid():
            with transaction.atomic():
                # Revertir stock anterior
                for detalle in self.object.detalles.all():
                    detalle.producto.cantidad_disponible += detalle.cantidad
                    detalle.producto.save()
                
                # Guardar cambios
                self.object = form.save(commit=False)
                total = 0
                
                formset.instance = self.object
                detalles = formset.save(commit=False)
                
                # Procesar detalles eliminados
                for detalle in formset.deleted_objects:
                    detalle.delete()
                
                # Guardar nuevos detalles
                for detalle in detalles:
                    if detalle.cantidad > detalle.producto.cantidad_disponible:
                        messages.error(
                            self.request,
                            f'No hay suficiente stock de {detalle.producto.nombre}'
                        )
                        return self.form_invalid(form)
                    
                    detalle.producto.cantidad_disponible -= detalle.cantidad
                    detalle.producto.save()
                    total += detalle.subtotal
                
                self.object.total = total
                self.object.save()
                
                for detalle in detalles:
                    detalle.save()
                
                messages.success(self.request, 'Venta actualizada exitosamente')
                return redirect(self.get_success_url())
        else:
            return self.form_invalid(form)


class CancelarVentaView(LoginRequiredMixin, FormView):
    template_name = 'ventas/cancelar_venta.html'
    form_class = CancelarVentaForm
    
    def dispatch(self, request, *args, **kwargs):
        self.venta = get_object_or_404(Venta, pk=kwargs['pk'])
        if self.venta.estado == 'CANCELADA':
            messages.warning(request, 'Esta venta ya está cancelada')
            return redirect('ventas:detalle_venta', pk=self.venta.pk)
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['venta'] = self.venta
        return context
    
    def form_valid(self, form):
        with transaction.atomic():
            # Revertir stock
            for detalle in self.venta.detalles.all():
                detalle.producto.cantidad_disponible += detalle.cantidad
                detalle.producto.save()
            
            # Actualizar venta
            self.venta.estado = 'CANCELADA'
            self.venta.motivo_cancelacion = form.cleaned_data['motivo']
            self.venta.fecha_cancelacion = timezone.now()
            self.venta.save()
            
            messages.success(self.request, 'Venta cancelada exitosamente')
            return redirect('ventas:detalle_venta', pk=self.venta.pk)
