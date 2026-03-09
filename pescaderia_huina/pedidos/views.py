import json
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.forms import inlineformset_factory
from django.db.models import Sum, Q, F
from django.template.loader import get_template
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from xhtml2pdf import pisa
from .models import Pedido, DetallePedido
from .forms import PedidoForm, DetallePedidoForm
from ventas.models import Venta
from productos.models import Producto
from proveedores.models import Proveedor

# Creamos la fábrica de formularios. Permite crear múltiples Detalles vinculados a 1 Pedido
DetallePedidoFormSet = inlineformset_factory(
    Pedido, 
    DetallePedido, 
    form=DetallePedidoForm, 
    extra=1, # Muestra 1 fila en blanco al cargar la página
    can_delete=True
)

@login_required
def lista_pedidos(request):
    pedidos = Pedido.objects.annotate(
        cantidad_total_calculada=Sum('detalles__cantidad') 
    ).order_by('-fecha')

    # Capturamos los parámetros de la URL
    query = request.GET.get('q')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    # 1. Filtro por texto (ID, Proveedor, NIT o Nombre del Producto)
    if query:
        pedidos = pedidos.filter(
            Q(id__icontains=query) | 
            Q(proveedor__nombre_contacto__icontains=query) | 
            Q(proveedor__nit__icontains=query) |
            Q(detalles__producto__nombre__icontains=query)
        ).distinct()

    # 2. Filtro por Rango de Fechas
    if fecha_inicio:
        pedidos = pedidos.filter(fecha__date__gte=fecha_inicio) 
    if fecha_fin:
        pedidos = pedidos.filter(fecha__date__lte=fecha_fin)    
        
    # ==========================================
    # 3. LÓGICA: EXPORTAR REPORTE A PDF
    # ==========================================
    if request.GET.get('export') == 'pdf':
        
        # --- LÓGICA PARA EL TÍTULO DEL RANGO DE FECHAS EN EL PDF ---
        if fecha_inicio and fecha_fin:
            texto_rango = f"Del {fecha_inicio} al {fecha_fin}"
        elif fecha_inicio:
            texto_rango = f"Desde el {fecha_inicio}"
        elif fecha_fin:
            texto_rango = f"Hasta el {fecha_fin}"
        else:
            meses = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
            mes_actual = timezone.now().month
            anio_actual = timezone.now().year
            texto_rango = f"{meses[mes_actual]} {anio_actual}"
        
        total_pedidos = pedidos.count()
        ordenes_confirmadas = pedidos.filter(estado__in=['REC', 'recibido']).count()
        ordenes_pendientes = pedidos.filter(estado__in=['PEN', 'pendiente']).count()
        ordenes_canceladas = pedidos.filter(estado__in=['CAN', 'cancelado']).count()
        suma_total = pedidos.aggregate(total=Sum('valor_total'))['total'] or 0

        context = {
            'pedidos': pedidos,
            'fecha_generacion': timezone.now(),
            'mes_reporte': texto_rango,                   
            'total_pedidos': total_pedidos,               
            'ordenes_confirmadas': ordenes_confirmadas,   
            'ordenes_pendientes': ordenes_pendientes,     
            'ordenes_canceladas': ordenes_canceladas,     
            'suma_total': suma_total                      
        }
        
        template = get_template('reporte_mensual_pdf.html') 
        html = template.render(context)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Reporte_Pedidos_Pescaderia.pdf"'
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('Hubo un error al generar el PDF del reporte', status=500)
            
        return response

    # ==========================================
    # 4. NUEVA LÓGICA: EXPORTAR REPORTE A EXCEL (CON DISEÑO)
    # ==========================================
    elif request.GET.get('export') == 'excel':
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Reporte_Pedidos_Pescaderia.xlsx"'
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Reporte de Pedidos"

        # --- Variables de Estilo ---
        borde_fino = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
        alineacion_centro = Alignment(horizontal="center", vertical="center")
        alineacion_derecha = Alignment(horizontal="right", vertical="center")
        
        # --- Lógica del rango de fechas para el título ---
        if fecha_inicio and fecha_fin: texto_rango = f"Del {fecha_inicio} al {fecha_fin}"
        elif fecha_inicio: texto_rango = f"Desde el {fecha_inicio}"
        elif fecha_fin: texto_rango = f"Hasta el {fecha_fin}"
        else: texto_rango = "Histórico Completo"

        # --- 1. ENCABEZADO PRINCIPAL (TÍTULO) ---
        ws.append(["REPORTE DE ÓRDENES DE PEDIDO"])
        ws.merge_cells('A1:G1') # Combina las celdas de la A a la G
        celda_titulo = ws['A1']
        celda_titulo.font = Font(name='Arial', size=14, bold=True, color="FFFFFF")
        celda_titulo.fill = PatternFill(start_color="0D6EFD", fill_type="solid") # Azul primario
        celda_titulo.alignment = alineacion_centro
        ws.row_dimensions[1].height = 25 # Altura de la fila
        
        # Subtítulo con fecha
        ws.append([f"Fecha de generación: {timezone.now().strftime('%d/%m/%Y %H:%M')} | Filtro: {texto_rango}"])
        ws.merge_cells('A2:G2')
        ws['A2'].font = Font(italic=True, color="6C757D")
        
        ws.append([]) # Fila 3 vacía para dar espacio
        
        # --- 2. ENCABEZADOS DE LA TABLA (Fila 4) ---
        encabezados = ['ID Pedido', 'Fecha', 'Proveedor', 'NIT', 'Estado', 'Uds.', 'Valor Total']
        ws.append(encabezados)
        
        for celda in ws[4]:
            celda.font = Font(bold=True, color="FFFFFF")
            celda.fill = PatternFill(start_color="343A40", fill_type="solid") # Fondo oscuro
            celda.alignment = alineacion_centro
            celda.border = borde_fino
            
        # --- 3. DATOS DE LA TABLA ---
        fila_actual = 5
        suma_unidades = 0
        suma_dinero = 0
        
        for p in pedidos:
            estado_texto = "Recibido" if p.estado in ['REC', 'recibido'] else "Pendiente" if p.estado in ['PEN', 'pendiente'] else "Cancelado"
            
            uds = p.cantidad_total_calculada or 0
            val = float(p.valor_total or 0)
            
            suma_unidades += uds
            suma_dinero += val
            
            ws.append([
                f"#{p.id}",
                p.fecha.strftime("%d/%m/%Y") if p.fecha else "",
                p.proveedor.nombre_contacto if p.proveedor else "N/A",
                p.proveedor.nit if p.proveedor else "N/A",
                estado_texto,
                uds,
                val
            ])
            
            # Aplicar estilos a la fila recién agregada
            for col_idx, celda in enumerate(ws[fila_actual], 1):
                celda.border = borde_fino
                
                # Alinear al centro: ID, Fecha, Estado, Uds
                if col_idx in [1, 2, 5, 6]:
                    celda.alignment = alineacion_centro
                    
                # Formato Moneda para el Total
                if col_idx == 7:
                    celda.number_format = '"$"#,##0'
                    
            # Dar color a la celda de Estado según su valor
            celda_estado = ws.cell(row=fila_actual, column=5)
            if estado_texto == "Recibido": celda_estado.font = Font(color="198754", bold=True) # Verde
            elif estado_texto == "Pendiente": celda_estado.font = Font(color="D97706", bold=True) # Naranja
            else: celda_estado.font = Font(color="DC3545", bold=True) # Rojo
            
            fila_actual += 1
            
        # --- 4. FILA DE TOTALES AL FINAL ---
        ws.append(["", "", "", "", "TOTAL GENERAL:", suma_unidades, suma_dinero])
        
        for col_idx, celda in enumerate(ws[fila_actual], 1):
            celda.font = Font(bold=True)
            if col_idx >= 5: # Borde solo en Totales
                celda.border = borde_fino
            if col_idx == 5: celda.alignment = alineacion_derecha
            if col_idx == 6: celda.alignment = alineacion_centro
            if col_idx == 7: celda.number_format = '"$"#,##0' # Formato Moneda
            
        # --- 5. AJUSTAR ANCHO DE COLUMNAS ---
        columnas_ancho = {'A': 12, 'B': 14, 'C': 35, 'D': 15, 'E': 15, 'F': 10, 'G': 18}
        for col, ancho in columnas_ancho.items():
            ws.column_dimensions[col].width = ancho

        wb.save(response)
        return response

    # 5. Si no es PDF ni Excel, renderiza la vista web normal
    return render(request, 'lista_pedidos.html', {'pedidos': pedidos})


@login_required
def crear_pedido(request):
    if request.method == 'POST':
        form_pedido = PedidoForm(request.POST)
        formset = DetallePedidoFormSet(request.POST) 
        
        if form_pedido.is_valid() and formset.is_valid():
            try:
                nuevo_pedido = form_pedido.save(commit=False)
                nuevo_pedido.valor_total = 0 
                nuevo_pedido.save() 
                
                total_general = 0
                detalles = formset.save(commit=False)
                
                for detalle in detalles:
                    detalle.pedido = nuevo_pedido 
                    
                    # LOGICA CORREGIDA: Detectar si es libras para cobrar la mitad en BD
                    factor = 0.5 if detalle.presentacion in ['libras', 'Lib', 'libra'] else 1
                    
                    subtotal = float(detalle.cantidad or 0) * float(detalle.precio_unitario or 0) * factor
                    total_general += subtotal
                    detalle.save()
                
                nuevo_pedido.valor_total = total_general
                nuevo_pedido.save()
                
                messages.success(request, f"Pedido #{nuevo_pedido.id} registrado con éxito.")
                return redirect('pedidos:lista_pedidos')
            except Exception as e:
                messages.error(request, f"Ocurrió un error: {e}")
        else:
            messages.error(request, "Por favor corrige los errores del formulario.")
    else:
        form_pedido = PedidoForm()
        formset = DetallePedidoFormSet()

    return render(request, 'crear_pedido.html', {
        'form_pedido': form_pedido,
        'formset': formset, 
    })


@login_required
def editar_pedido(request, id):
    pedido = get_object_or_404(Pedido, id=id)
    
    # --- BLOQUEO DE SEGURIDAD BACKEND ---
    if pedido.estado in ['REC', 'recibido', 'CAN', 'cancelado']:
        messages.error(request, f"Acción denegada: El pedido #{pedido.id} ya no se puede modificar porque se encuentra {pedido.get_estado_display() if hasattr(pedido, 'get_estado_display') else pedido.estado}.")
        return redirect('pedidos:lista_pedidos')
    # ------------------------------------

    if request.method == 'POST':
        form_pedido = PedidoForm(request.POST, instance=pedido)
        formset = DetallePedidoFormSet(request.POST, instance=pedido)

        if form_pedido.is_valid() and formset.is_valid():
            pedido_obj = form_pedido.save(commit=False)
            formset.save()
            
            # LOGICA CORREGIDA: Recalcular sumando iterativamente para no saltarnos la validación de Libras
            total_recalculado = 0
            for d in pedido_obj.detalles.all():
                factor = 0.5 if d.presentacion in ['libras', 'Lib', 'libra'] else 1
                total_recalculado += float(d.cantidad or 0) * float(d.precio_unitario or 0) * factor
                
            pedido_obj.valor_total = total_recalculado
            pedido_obj.save()
            
            messages.info(request, f"Pedido #{pedido.id} actualizado correctamente.")
            return redirect('pedidos:lista_pedidos')
    else:
        form_pedido = PedidoForm(instance=pedido)
        formset = DetallePedidoFormSet(instance=pedido)

    return render(request, 'editar_pedido.html', {
        'form_pedido': form_pedido,
        'formset': formset,
        'pedido': pedido
    })


@login_required
def eliminar_pedido(request, id):
    pedido = get_object_or_404(Pedido, id=id)
    if request.method == 'POST':
        pedido.delete()
        messages.warning(request, f"El pedido #{id} ha sido eliminado.")
        return redirect('pedidos:lista_pedidos')
    return render(request, 'eliminar_pedido.html', {'pedido': pedido})


# VER DETALLES DEL PEDIDO
@login_required
def detalle_pedido(request, id):
    pedido = get_object_or_404(Pedido, id=id)
    
    if request.GET.get('export') == 'pdf':
        detalles_con_subtotal = []
        for d in pedido.detalles.all():
            cant = float(d.cantidad or 0)
            prec = float(d.precio_unitario or 0)
            
            # LOGICA CORREGIDA: Aplicar factor de libras en el PDF
            factor = 0.5 if d.presentacion in ['libras', 'Lib', 'libra'] else 1
            
            d.subtotal_calculado = cant * prec * factor
            detalles_con_subtotal.append(d)
            
        template = get_template('pdf_pedido.html')
        html = template.render({
            'pedido': pedido, 
            'detalles': detalles_con_subtotal 
        })
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Pedido_{pedido.id}.pdf"'
        
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('Hubo un error al generar el PDF', status=500)
            
        return response

    return render(request, 'detalle_pedido.html', {
        'pedido': pedido
    })
    

@login_required
def cargar_productos_proveedor(request):
    proveedor_id = request.GET.get('proveedor_id')
    
    if proveedor_id:
        productos = Producto.objects.filter(proveedor_id=proveedor_id).order_by('nombre')
        data = list(productos.values('id', 'nombre'))
    else:
        data = []
        
    return JsonResponse(data, safe=False)


# ==========================================
# CAMBIAR ESTADO DESDE LA LISTA
# ==========================================
@login_required
@require_POST
def cambiar_estado_pedido(request, pedido_id):
    try:
        data = json.loads(request.body)
        nuevo_estado = data.get('estado')
        
        pedido = get_object_or_404(Pedido, id=pedido_id)
        
        estados_validos = ['recibido', 'cancelado', 'pendiente', 'REC', 'CAN', 'PEN']
        
        if nuevo_estado in estados_validos:
            pedido.estado = nuevo_estado
            pedido.save()
            return JsonResponse({'success': True, 'estado': nuevo_estado})
        else:
            return JsonResponse({'success': False, 'error': 'Estado no válido'})
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
@login_required
def inventario_pedidos(request):
    """Vista de inventario con datos sincronizados desde pedidos y alertas funcionales."""
    productos = Producto.objects.filter(estado=True)
    
    def calcular_stock_y_pedidos(queryset):
        for p in queryset:
            # Stock recibido: suma de pedidos REC
            stock_recibido = DetallePedido.objects.filter(producto=p, pedido__estado='REC').aggregate(total=Sum('cantidad'))['total'] or 0
            # Ventas completadas: suma de ventas COMPLETADAS
            from ventas.models import Venta
            ventas_completadas = Venta.objects.filter(producto=p, estado='COMPLETADA').aggregate(total=Sum('cantidad'))['total'] or 0
            # Stock disponible: recibido - vendido (mínimo 0)
            p.stock_disponible = max(0, stock_recibido - ventas_completadas)
        return queryset
    
    pescados = calcular_stock_y_pedidos(productos.filter(tipo_producto='PE'))
    mariscos = calcular_stock_y_pedidos(productos.filter(tipo_producto='MA'))
    pollos = calcular_stock_y_pedidos(productos.filter(tipo_producto='PO'))
    
    # EXPORTAR A PDF
    if request.GET.get('export') == 'pdf':
        template = get_template('inventario_pdf.html')
        context = {
            'pescados': pescados,
            'mariscos': mariscos,
            'pollos': pollos,
            'fecha_generacion': timezone.now(),
        }
        html = template.render(context)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Inventario_Pescaderia.pdf"'
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('Hubo un error al generar el PDF', status=500)
        return response
    
    # EXPORTAR A EXCEL
    elif request.GET.get('export') == 'excel':
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Inventario_Pescaderia.xlsx"'
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Inventario"
        
        # Estilos
        borde_fino = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
        alineacion_centro = Alignment(horizontal="center", vertical="center")
        
        # Encabezado principal
        ws.append(["INVENTARIO DE PRODUCTOS"])
        ws.merge_cells('A1:D1')
        celda_titulo = ws['A1']
        celda_titulo.font = Font(name='Arial', size=14, bold=True, color="FFFFFF")
        celda_titulo.fill = PatternFill(start_color="0D6EFD", fill_type="solid")
        celda_titulo.alignment = alineacion_centro
        ws.row_dimensions[1].height = 25
        
        # Subtítulo
        ws.append([f"Generado: {timezone.now().strftime('%d/%m/%Y %H:%M')}"])
        ws.merge_cells('A2:D2')
        ws['A2'].font = Font(italic=True, color="6C757D")
        
        ws.append([])
        
        fila = 4
        
        # Función para crear sección
        def agregar_seccion(titulo, productos_list):
            nonlocal fila
            
            # Título de categoría
            ws.append([titulo])
            ws.merge_cells(f'A{fila}:D{fila}')
            celda_cat = ws[f'A{fila}']
            celda_cat.font = Font(bold=True, color="FFFFFF", size=11)
            celda_cat.fill = PatternFill(start_color="343A40", fill_type="solid")
            celda_cat.alignment = alineacion_centro
            fila += 1
            
            # Encabezados
            encabezados = ['Nombre', 'Proveedor', 'Stock Disponible', 'Presentación']
            ws.append(encabezados)
            
            for celda in ws[fila]:
                celda.font = Font(bold=True, color="FFFFFF")
                celda.fill = PatternFill(start_color="6C757D", fill_type="solid")
                celda.alignment = alineacion_centro
                celda.border = borde_fino
            
            fila += 1
            
            # Datos
            for p in productos_list:
                ws.append([
                    p.nombre,
                    p.proveedor.nombre_contacto if p.proveedor else "N/A",
                    p.stock_disponible,
                    p.get_tipo_presentacion_display()
                ])
                
                for celda in ws[fila]:
                    celda.border = borde_fino
                    celda.alignment = alineacion_centro
                
                fila += 1
            
            ws.append([])
            fila += 1
        
        # Agregar secciones
        agregar_seccion("PESCADOS", pescados)
        agregar_seccion("MARISCOS", mariscos)
        agregar_seccion("POLLOS", pollos)
        
        # Ajustar anchos de columna
        ws.column_dimensions['A'].width = 25
        ws.column_dimensions['B'].width = 20
        ws.column_dimensions['C'].width = 18
        ws.column_dimensions['D'].width = 25
        
        wb.save(response)
        return response
    
    context = {
        'pescados': pescados,
        'mariscos': mariscos,
        'pollos': pollos,
    }
    
    return render(request, 'inventario_pedidos.html', context)
