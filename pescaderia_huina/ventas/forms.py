from django import forms
from .models import Venta
from productos.models import Producto

class VentaForm(forms.ModelForm):
    
    class Meta:
        model = Venta
        fields = [
            'nombre_cliente',
            'documento_cliente',
            'producto',
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
        
        if producto and cantidad:
            # Validar stock disponible
            if cantidad > producto.stock:
                raise forms.ValidationError(
                    f'No hay suficiente stock. Disponible: {producto.stock}'
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
    fecha_inicio = forms.DateField(
        required=False,
        label='Fecha Inicio',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    fecha_fin = forms.DateField(
        required=False,
        label='Fecha Fin',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    estado = forms.ChoiceField(
        required=False,
        label='Estado',
        choices=[('', 'Todos')] + Venta.ESTADOS,
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