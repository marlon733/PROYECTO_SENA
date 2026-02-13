from django import forms
from .models import Venta
from productos.models import Producto


TIPOS_VENTA_CHOICES = [
    ('EMPACADO_VACIO', 'Empacado al Vacío'),
    ('POR_LIBRA', 'Por Libra'),
    ('BANDEJA', 'Bandeja'),
]

class VentaForm(forms.ModelForm):
    
    class Meta:
        model = Venta
        fields = [
            'nombre_cliente',
            'documento_cliente',
            'producto',
            'tipo_presentacion',
            'cantidad',
            'precio_unitario',
            'observaciones'
        ]
        widgets = {
            'nombre_cliente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre del cliente'
            }),
            'documento_cliente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el documento del cliente'
            }),
            'producto': forms.Select(attrs={
                'class': 'form-select'
            }),
             'tipo_presentacion': forms.RadioSelect(attrs={
                'class': 'tipo-presentacion-radio',
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': 'Cantidad'
            }),
            'precio_unitario': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': 'Precio unitario'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones opcionales sobre la venta...'
            })
        }
        labels = {
            'nombre_cliente': 'Nombre del Cliente',
            'documento_cliente': 'Documento de Identidad',
            'producto': 'Producto',
            'tipo_presentacion': 'Tipo de Presentación',
            'cantidad': 'Cantidad',
            'precio_unitario': 'Precio Unitario',
            'observaciones': 'Observaciones'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo productos activos con stock
        self.fields['producto'].queryset = Producto.objects.filter(
            estado=True, 
            stock__gt=0
        )

    # Validaciones personalizadas
    def clean_documento_cliente(self):
        """Validar que el documento contenga solo números"""
        documento = self.cleaned_data.get('documento_cliente')
        if not documento.isdigit():
            raise forms.ValidationError("El documento debe contener solo números.")
        return documento

    
    def clean(self):
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        cantidad = cleaned_data.get('cantidad')
        tipo_presentacion = cleaned_data.get('tipo_presentacion')
        
        if producto and cantidad:
            # Validar stock disponible
            if cantidad > producto.stock:
                raise forms.ValidationError(
                    f'No hay suficiente stock. Disponible: {producto.stock}'
                )
                
         # Empacado al Vacío y Bandeja deben ser unidades enteras
        if cantidad and tipo_presentacion in ('EMPACADO_VACIO', 'BANDEJA'):
            if cantidad != int(cantidad):
                raise forms.ValidationError(
                    'Para Empacado al Vacío y Bandeja, la cantidad debe ser un número entero de unidades.'
                )
        
        return cleaned_data


class CancelarVentaForm(forms.Form):
    """Formulario para cancelar una venta"""
    motivo = forms.CharField(
        label='Motivo de Cancelación',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Escriba el motivo de la cancelación (mínimo 10 caracteres)...'
        }),
        min_length=10,
        error_messages={
            'required': 'Debe proporcionar un motivo para cancelar la venta',
            'min_length': 'El motivo debe tener al menos 10 caracteres'
        }
    )


class BusquedaVentaForm(forms.Form):
    """Formulario para buscar y filtrar ventas"""
    estado = forms.ChoiceField(
        required=False,
        label='Estado',
        choices=[('', 'Todos')] + Venta.ESTADOS,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    tipo_presentacion = forms.ChoiceField(
        required=False,
        label='Tipo de Presentación',
        choices=[('', 'Todos los tipos')] + Venta.TIPO_PRESENTACION,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    buscar = forms.CharField(
        required=False,
        label='Buscar',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre de cliente o documento...'
        })
    )