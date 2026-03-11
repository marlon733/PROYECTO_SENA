from django import forms
from django.forms import inlineformset_factory
from .models import Venta, VentaItem
from productos.models import Producto


class VentaForm(forms.ModelForm):
    """Formulario principal de venta (solo datos del cliente y observaciones)"""

    class Meta:
        model = Venta
        fields = ['nombre_cliente', 'documento_cliente', 'observaciones']
        widgets = {
            'nombre_cliente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre del cliente (opcional)'
            }),
            'documento_cliente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Documento del cliente (opcional)'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones opcionales...'
            })
        }
        labels = {
            'nombre_cliente': 'Nombre del Cliente',
            'documento_cliente': 'Documento de Identidad',
            'observaciones': 'Observaciones'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cliente completamente opcional
        self.fields['nombre_cliente'].required = False
        self.fields['documento_cliente'].required = False

    def clean_documento_cliente(self):
        documento = self.cleaned_data.get('documento_cliente')
        if documento and not documento.isdigit():
            raise forms.ValidationError("El documento debe contener solo números.")
        return documento


class VentaItemForm(forms.ModelForm):

    class Meta:
        model = VentaItem
        fields = ['producto', 'tipo_presentacion', 'cantidad', 'precio_unitario']
        widgets = {
            'producto': forms.Select(attrs={
                'class': 'form-select producto-select',
            }),
            'tipo_presentacion': forms.Select(attrs={
                'class': 'form-select tipo-presentacion-select'
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control cantidad-input',
                'step': '0.01',
                'min': '0.01',
                'placeholder': 'Cantidad'
            }),
            #  precio_unitario se hereda del producto via JS, pero editable
            'precio_unitario': forms.NumberInput(attrs={
                'class': 'form-control precio-input',
                'step': '0.01',
                'min': '0.01',
                'placeholder': 'Precio unitario'
            }),
        }
        labels = {
            'producto': 'Producto',
            'tipo_presentacion': 'Presentación',
            'cantidad': 'Cantidad',
            'precio_unitario': 'Precio de Venta',  # ✅ REQ 2: Renombrado
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo productos activos
        self.fields['producto'].queryset = Producto.objects.filter(estado=True).select_related('proveedor')
        self.fields['producto'].empty_label = "-- Seleccionar producto --"

    def clean(self):
        cleaned_data = super().clean()
        cantidad = cleaned_data.get('cantidad')
        tipo_presentacion = cleaned_data.get('tipo_presentacion')

        if cantidad and tipo_presentacion in ('EMPACADO_VACIO', 'BANDEJA'):
            from decimal import Decimal
            if cantidad != int(cantidad):
                raise forms.ValidationError(
                    'Para Empacado al Vacío y Bandeja, la cantidad debe ser un número entero.'
                )
        return cleaned_data


# múltiples productos
VentaItemFormSet = inlineformset_factory(
    Venta,
    VentaItem,
    form=VentaItemForm,
    extra=0,
    min_num=1,
    validate_min=True,
    can_delete=True,
)


class CancelarVentaForm(forms.Form):
    motivo = forms.CharField(
        label='Motivo de Cancelación (opcional)',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Escriba el motivo de la cancelación (opcional)...'
        }),
        required=False, 
    )


class BusquedaVentaForm(forms.Form):
    estado = forms.ChoiceField(
        required=False,
        label='Estado',
        choices=[
            ('', 'Todos'),
            ('COMPLETADA', 'Completada'),
            ('CANCELADA', 'Cancelada'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    buscar = forms.CharField(
        required=False,
        label='Buscar',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre de cliente, documento o producto...'
        })
    )
    # campos de fecha
    fecha_inicio = forms.DateField(
        required=False,
        label='Fecha inicio',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    fecha_fin = forms.DateField(
        required=False,
        label='Fecha fin',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )