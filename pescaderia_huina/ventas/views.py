from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views import generic
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Sum
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

from .models import Venta, VentaItem
from .forms import VentaForm, VentaItemFormSet, CancelarVentaForm, BusquedaVentaForm
from productos.models import Producto


@login_required
def buscar_productos_api(request):
    q = request.GET.get('q', '')
    tipo = request.GET.get('tipo', '')   
    productos = Producto.objects.filter(estado=True).select_related('proveedor')
    if tipo:
        productos = productos.filter(tipo_producto=tipo)
    if q:
        productos = productos.filter(nombre__icontains=q)
    data = [
        {'id': p.id, 'nombre': p.nombre, 'precio': str(p.precio)}
        for p in productos[:20]
    ]
    return JsonResponse({'productos': data})

@login_required
def precio_producto_api(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, estado=True)
    return JsonResponse({'precio': str(producto.precio), 'nombre': producto.nombre, 'stock': str(producto.stock)})


@login_required
def ventas(request):
    lista_ventas = Venta.objects.prefetch_related('items__producto').all()
    form_busqueda = BusquedaVentaForm(request.GET)
    if form_busqueda.is_valid():
        estado = form_busqueda.cleaned_data.get('estado')
        buscar = form_busqueda.cleaned_data.get('buscar')
        if estado:
            lista_ventas = lista_ventas.filter(estado=estado)
        if buscar:
            lista_ventas = lista_ventas.filter(
                Q(nombre_cliente__icontains=buscar) |
                Q(documento_cliente__icontains=buscar) |
                Q(items__producto__nombre__icontains=buscar)
            ).distinct()

    total_ventas = Venta.objects.filter(estado='COMPLETADA').count()
    total_ingresos = Venta.objects.filter(estado='COMPLETADA').aggregate(total=Sum('total'))['total'] or 0

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
    return render(request, 'detalle_venta.html', {'venta': venta})


class VentaCreateView(LoginRequiredMixin, generic.CreateView):
    model = Venta
    form_class = VentaForm
    template_name = 'crear_venta.html'
    success_url = reverse_lazy('ventas:lista_ventas')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['item_formset'] = VentaItemFormSet(self.request.POST)
        else:
            context['item_formset'] = VentaItemFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        item_formset = context['item_formset']
        if not item_formset.is_valid():
            messages.error(self.request, 'Corrija los errores en los productos.')
            return self.render_to_response(context)
        with transaction.atomic():
            venta = form.save()
            items = item_formset.save(commit=False)
            for item in items:
                item.venta = venta
                item.save()
            for obj in item_formset.deleted_objects:
                obj.delete()
            venta.recalcular_totales()
            messages.success(self.request, f'Venta {venta.id} registrada. Total: ${venta.total:,.2f}')
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
            messages.warning(request, 'No se puede editar una venta cancelada.')
            return redirect('ventas:detalle_venta', id_venta=venta.id)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['item_formset'] = VentaItemFormSet(self.request.POST, instance=self.object)
        else:
            context['item_formset'] = VentaItemFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        item_formset = context['item_formset']
        if not item_formset.is_valid():
           messages.error(self.request, 'Corrija los errores en los productos.')
           return self.render_to_response(context)
        with transaction.atomic():
            venta = form.save()
            for item_form in item_formset:
                if not item_form.cleaned_data:
                   continue
                if item_form.cleaned_data.get('DELETE') and item_form.instance.pk:
                   item_form.instance.delete()  # ✅ sin restaurar stock
                continue
            if item_form.cleaned_data.get('producto'):
                item = item_form.save(commit=False)
                item.venta = venta
                item.save()  # ✅ sin ajuste de stock
            venta.recalcular_totales()
            messages.success(self.request, f'Venta #{venta.id} actualizada exitosamente.')
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
            messages.warning(request, 'Esta venta ya está cancelada.')
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
        # ✅ Sin tocar stock — se recalcula solo al cambiar estado a CANCELADA
          motivo = form.cleaned_data.get('motivo') or 'Sin motivo especificado'
          self.venta.estado = 'CANCELADA'
          self.venta.motivo_cancelacion = motivo
          self.venta.fecha_cancelacion = timezone.now()
          self.venta.save(update_fields=['estado', 'motivo_cancelacion', 'fecha_cancelacion'])
          messages.success(self.request, f'Venta #{self.venta.id} cancelada exitosamente.')
        return super().form_valid(form)


@login_required
def exportar_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Ventas"

    azul_oscuro = "0A3D62"
    verde = "198754"
    gris_claro = "F2F2F2"

    header_font = Font(bold=True, color="FFFFFF", size=10)
    header_fill = PatternFill(start_color=azul_oscuro, end_color=azul_oscuro, fill_type="solid")
    center_align = Alignment(horizontal='center', vertical='center', wrap_text=True)
    left_align = Alignment(horizontal='left', vertical='center', wrap_text=True)
    right_align = Alignment(horizontal='right', vertical='center')
    thin_border = Border(
        left=Side(style='thin', color='CCCCCC'),
        right=Side(style='thin', color='CCCCCC'),
        top=Side(style='thin', color='CCCCCC'),
        bottom=Side(style='thin', color='CCCCCC'),
    )

    # Título
    ws.merge_cells('A1:I1')
    ws['A1'].value = 'REPORTE DE VENTAS — PESCADERÍA HUINA'
    ws['A1'].font = Font(bold=True, color="FFFFFF", size=13)
    ws['A1'].fill = PatternFill(start_color=azul_oscuro, end_color=azul_oscuro, fill_type="solid")
    ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[1].height = 28

    # Estadísticas
    total_completadas = Venta.objects.filter(estado='COMPLETADA').count()
    total_ingresos = Venta.objects.filter(estado='COMPLETADA').aggregate(t=Sum('total'))['t'] or Decimal('0')
    ws.merge_cells('A2:D2')
    ws['A2'] = f'Ventas Completadas: {total_completadas}'
    ws['A2'].font = Font(bold=True, size=10)
    ws['A2'].fill = PatternFill(start_color="E8F4F8", end_color="E8F4F8", fill_type="solid")
    ws['A2'].alignment = center_align
    ws.merge_cells('E2:I2')
    ws['E2'] = f'Ingresos Totales: ${total_ingresos:,.2f}'
    ws['E2'].font = Font(bold=True, size=10, color=verde)
    ws['E2'].fill = PatternFill(start_color="E8F4F8", end_color="E8F4F8", fill_type="solid")
    ws['E2'].alignment = center_align
    ws.row_dimensions[2].height = 20

    # Cabecera
    headers = ['#', 'Cliente', 'Documento', 'Productos', 'Subtotal', 'IVA (19%)', 'Total', 'Fecha', 'Estado']
    col_widths = [7, 25, 18, 45, 14, 14, 14, 20, 14]
    for col, (header, width) in enumerate(zip(headers, col_widths), 1):
        cell = ws.cell(row=3, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_align
        cell.border = thin_border
        ws.column_dimensions[openpyxl.utils.get_column_letter(col)].width = width
    ws.row_dimensions[3].height = 18

    # Datos
    ventas_qs = Venta.objects.prefetch_related('items__producto').all()
    for row_num, venta in enumerate(ventas_qs, 4):
        items = venta.items.all()
        productos_str = '\n'.join(
            f"{item.producto.nombre} x{item.cantidad} @ ${item.precio_unitario}" for item in items
        ) if items.exists() else (str(venta.producto.nombre) if venta.producto else 'N/A')

        row_data = [
            venta.id,
            venta.nombre_cliente or 'Anónimo',
            venta.documento_cliente or 'N/A',
            productos_str,
            float(venta.subtotal or 0),
            float(venta.iva_monto or 0),
            float(venta.total or 0),
            venta.fecha_venta.strftime('%d/%m/%Y %H:%M'),
            venta.estado,
        ]

        if venta.estado == 'CANCELADA':
            bg = PatternFill(start_color="FFE0E0", end_color="FFE0E0", fill_type="solid")
        elif row_num % 2 == 0:
            bg = PatternFill(start_color=gris_claro, end_color=gris_claro, fill_type="solid")
        else:
            bg = None

        for col, value in enumerate(row_data, 1):
            cell = ws.cell(row=row_num, column=col, value=value)
            cell.border = thin_border
            if bg:
                cell.fill = bg
            if col == 1:
                cell.alignment = center_align
            elif col in (5, 6, 7):
                cell.alignment = right_align
                cell.number_format = '$#,##0.00'
            elif col == 4:
                cell.alignment = left_align
            else:
                cell.alignment = center_align
            if col == 9:
                if venta.estado == 'CANCELADA':
                    cell.font = Font(bold=True, color="DC2626")
                elif venta.estado == 'COMPLETADA':
                    cell.font = Font(bold=True, color=verde)

        ws.row_dimensions[row_num].height = max(15, min(60, 15 * (productos_str.count('\n') + 1)))

    ws.freeze_panes = 'A4'

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="ventas_pescaderia_huina.xlsx"'
    wb.save(response)
    return response


@login_required
def exportar_pdf(request):
    from reportlab.lib.pagesizes import landscape, A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from io import BytesIO
    import datetime

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4),
        rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)

    styles = getSampleStyleSheet()
    AZUL = colors.HexColor('#0a3d62')
    VERDE = colors.HexColor('#198754')
    ROJO = colors.HexColor('#dc2626')
    GRIS = colors.HexColor('#6c757d')
    ROJO_CLARO = colors.HexColor('#fde8e8')

    titulo_style = ParagraphStyle('titulo', parent=styles['Title'], fontSize=18,
        textColor=AZUL, spaceAfter=2, alignment=TA_CENTER, fontName='Helvetica-Bold')
    subtitulo_style = ParagraphStyle('subtitulo', parent=styles['Normal'], fontSize=9,
        textColor=GRIS, alignment=TA_CENTER, spaceAfter=14)
    prod_style = ParagraphStyle('prod', fontSize=7, leading=10, alignment=TA_LEFT)

    story = []
    story.append(Paragraph("Pescadería Huina", titulo_style))
    story.append(Paragraph(
        f"Reporte de Ventas — Generado el {datetime.datetime.now().strftime('%d/%m/%Y a las %H:%M')}",
        subtitulo_style
    ))
    story.append(HRFlowable(width="100%", thickness=2, color=AZUL, spaceAfter=14))

    total_completadas = Venta.objects.filter(estado='COMPLETADA').count()
    total_ingresos = Venta.objects.filter(estado='COMPLETADA').aggregate(t=Sum('total'))['t'] or Decimal('0')
    total_canceladas = Venta.objects.filter(estado='CANCELADA').count()

    stats_data = [
        ['Ventas Completadas', 'Ingresos Totales', 'Ventas Canceladas'],
        [str(total_completadas), f"${total_ingresos:,.2f}", str(total_canceladas)],
    ]
    stats_table = Table(stats_data, colWidths=[7*cm, 8*cm, 7*cm])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), AZUL),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#e8f4f8')),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, 1), 14),
        ('TEXTCOLOR', (0, 1), (0, 1), AZUL),
        ('TEXTCOLOR', (1, 1), (1, 1), VERDE),
        ('TEXTCOLOR', (2, 1), (2, 1), ROJO),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
    ]))
    story.append(stats_table)
    story.append(Spacer(1, 16))

    headers = ['Cliente', 'Documento', 'Productos', 'Subtotal', 'IVA (19%)', 'Total', 'Fecha', 'Estado']
    col_widths = [1*cm, 4.2*cm, 2.8*cm, 7.5*cm, 2.4*cm, 2.4*cm, 2.4*cm, 3.0*cm, 2.3*cm]

    data = [headers]
    ventas_qs = Venta.objects.prefetch_related('items__producto').all()
    for venta in ventas_qs:
        items = venta.items.all()
        prods_text = '\n'.join(f"{item.producto.nombre} x{item.cantidad}" for item in items) \
            if items.exists() else (str(venta.producto.nombre) if venta.producto else 'N/A')
        data.append([
            str(venta.id),
            venta.nombre_cliente or 'Anónimo',
            venta.documento_cliente or 'N/A',
            Paragraph(prods_text, prod_style),
            f"${(venta.subtotal or Decimal('0')):,.2f}",
            f"${(venta.iva_monto or Decimal('0')):,.2f}",
            f"${(venta.total or Decimal('0')):,.2f}",
            venta.fecha_venta.strftime('%d/%m/%Y\n%H:%M'),
            venta.estado,
        ])

    tabla = Table(data, colWidths=col_widths, repeatRows=1)
    row_styles = [
        ('BACKGROUND', (0, 0), (-1, 0), AZUL),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('ALIGN', (0, 1), (2, -1), 'CENTER'),
        ('ALIGN', (4, 1), (6, -1), 'RIGHT'),
        ('ALIGN', (7, 1), (8, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#dee2e6')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]
    for i, row in enumerate(data[1:], 1):
        estado_val = row[8] if isinstance(row[8], str) else ''
        if estado_val == 'CANCELADA':
            row_styles.append(('BACKGROUND', (0, i), (-1, i), ROJO_CLARO))
            row_styles.append(('TEXTCOLOR', (8, i), (8, i), ROJO))
            row_styles.append(('FONTNAME', (8, i), (8, i), 'Helvetica-Bold'))
        elif estado_val == 'COMPLETADA':
            bg = colors.HexColor('#f8fffe') if i % 2 == 0 else colors.white
            row_styles.append(('BACKGROUND', (0, i), (-1, i), bg))
            row_styles.append(('TEXTCOLOR', (8, i), (8, i), VERDE))
            row_styles.append(('FONTNAME', (8, i), (8, i), 'Helvetica-Bold'))

    tabla.setStyle(TableStyle(row_styles))
    story.append(tabla)
    doc.build(story)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="ventas_pescaderia_huina.pdf"'
    return response