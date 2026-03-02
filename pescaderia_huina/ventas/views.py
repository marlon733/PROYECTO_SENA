from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import get_template
from django.http import HttpResponse
from django.views import generic
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Sum
from django.db import transaction
from django.utils import timezone
from xhtml2pdf import pisa
from .models import Venta
from .forms import VentaForm, CancelarVentaForm, BusquedaVentaForm
from productos.models import Producto


def _aplicar_filtros(queryset, form):
    if not form.is_valid():
        return queryset
    estado = form.cleaned_data.get('estado')
    buscar = form.cleaned_data.get('buscar')
    fecha_inicio = form.cleaned_data.get('fecha_inicio')
    fecha_fin = form.cleaned_data.get('fecha_fin')

    if estado:
        queryset = queryset.filter(estado=estado)
    if buscar:
        queryset = queryset.filter(
            Q(nombre_cliente__icontains=buscar) |
            Q(documento_cliente__icontains=buscar) |
            Q(producto__nombre__icontains=buscar)
        )
    if fecha_inicio:
        queryset = queryset.filter(fecha_venta__date__gte=fecha_inicio)
    if fecha_fin:
        queryset = queryset.filter(fecha_venta__date__lte=fecha_fin)
    return queryset


@login_required
def ventas(request):
    lista_ventas = Venta.objects.all()
    form_busqueda = BusquedaVentaForm(request.GET)
    lista_ventas = _aplicar_filtros(lista_ventas, form_busqueda)

    if request.GET.get('export') == 'pdf':
        template = get_template('pdf_ventas.html')
        pdf_ventas = list(lista_ventas)
        html = template.render({
            'ventas': pdf_ventas,
            'fecha_reporte': timezone.now(),
            'mes_actual': timezone.now().strftime('%B %Y'),
            'total_ventas': len(pdf_ventas),
            'ventas_completadas': sum(1 for v in pdf_ventas if v.estado == 'COMPLETADA'),
            'ventas_pendientes': sum(1 for v in pdf_ventas if v.estado == 'PENDIENTE'),
            'ventas_canceladas': sum(1 for v in pdf_ventas if v.estado == 'CANCELADA'),
            'total_ingresos': sum(v.total or 0 for v in pdf_ventas if v.estado == 'COMPLETADA'),
        })
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Reporte_Ventas.pdf"'
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('Error al generar PDF', status=500)
        return response
    

    # Estadísticas globales (no filtradas)
    total_ventas = Venta.objects.filter(estado='COMPLETADA').count()
    total_ingresos = Venta.objects.filter(estado='COMPLETADA').aggregate(
        total=Sum('total')
    )['total'] or 0

    context = {
        'lista_ventas': lista_ventas,
        'form_busqueda': form_busqueda,
        'total_ventas': total_ventas,
        'total_ingresos': total_ingresos,
    }
    return render(request, 'lista_ventas.html', context)


@login_required
def detalle_venta(request, id_venta):
    venta = get_object_or_404(Venta, id=id_venta)

    if request.GET.get('export') == 'pdf':
        template = get_template('pdf_ventas.html')
        html = template.render({
            'ventas': [venta],
            'fecha_reporte': timezone.now(),
            'mes_actual': timezone.now().strftime('%B %Y'),
            'total_ventas': 1,
            'ventas_completadas': 1 if venta.estado == 'COMPLETADA' else 0,
            'ventas_pendientes': 1 if venta.estado == 'PENDIENTE' else 0,
            'ventas_canceladas': 1 if venta.estado == 'CANCELADA' else 0,
            'total_ingresos': venta.total or 0,
        })
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Venta_{venta.id}.pdf"'
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('Error al generar PDF', status=500)
        return response

    return render(request, 'detalle_venta.html', {'venta': venta})


class VentaCreateView(LoginRequiredMixin, generic.CreateView):
    model = Venta
    form_class = VentaForm
    template_name = 'crear_venta.html'
    success_url = reverse_lazy('ventas:lista_ventas')

    def form_valid(self, form):
        with transaction.atomic():
            venta = form.save()
            messages.success(
                self.request,
                f'La venta #{venta.id} para {venta.nombre_cliente} ha sido registrada exitosamente.'
            )
            return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, 'Por favor, corrija los errores en el formulario.')
        return super().form_invalid(form)


class VentaUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Venta
    form_class = VentaForm
    template_name = 'editar_venta.html'
    success_url = reverse_lazy('ventas:lista_ventas')
    pk_url_kwarg = 'venta_id'

    def dispatch(self, request, *args, **kwargs):
        venta = self.get_object()
        if venta.estado == 'CANCELADA':
            messages.warning(request, 'No se puede editar una venta cancelada')
            return redirect('ventas:detalle_venta', id_venta=venta.id)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        with transaction.atomic():
            venta = form.save()
            messages.success(
                self.request,
                f'La venta #{venta.id} ha sido actualizada exitosamente.'
            )
            return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, 'Por favor, corrija los errores en el formulario.')
        return super().form_invalid(form)


class VentaCancelarView(LoginRequiredMixin, generic.FormView):
    template_name = 'cancelar_venta.html'
    form_class = CancelarVentaForm

    def dispatch(self, request, *args, **kwargs):
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
        with transaction.atomic():
            self.venta.estado = 'CANCELADA'
            self.venta.motivo_cancelacion = form.cleaned_data['motivo']
            self.venta.fecha_cancelacion = timezone.now()
            self.venta.save()
            messages.success(
                self.request,
                f'La venta #{self.venta.id} ha sido cancelada exitosamente.'
            )
        return super().form_valid(form)