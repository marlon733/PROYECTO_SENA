from django import forms
from django.forms import inlineformset_factory
from .models import Venta, DetalleVenta, Producto
from decimal import Decimal


class VentaForm(forms.ModelForm):
    """
    Formulario para crear y editar ventas (Historia #10)
    """
    
    class Meta:
        model = Venta
        fields = ['observaciones']
        
        widgets = {
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Observaciones adicionales (opcional)',
                'rows': 3
            }),
        }
        
        labels = {
            'observaciones': 'Observaciones',
        }


class DetalleVentaForm(forms.ModelForm):
    """
    Formulario para agregar productos a una venta (Historia #10)
    Incluye validaciones según Historia #21
    """
    
    class Meta:
        model = DetalleVenta
        fields = ['producto', 'cantidad', 'precio_unitario']
        
        widgets = {
            'producto': forms.Select(attrs={
                'class': 'form-control producto-select',
                'required': True
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control cantidad-input',
                'placeholder': 'Cantidad',
                'step': '0.01',
                'min': '0.01',
                'required': True
            }),
            'precio_unitario': forms.NumberInput(attrs={
                'class': 'form-control precio-input',
                'placeholder': 'Precio unitario',
                'step': '0.01',
                'min': '0.01',
                'required': True,
                'readonly': True
            }),
        }
        
        labels = {
            'producto': 'Producto',
            'cantidad': 'Cantidad',
            'precio_unitario': 'Precio Unitario',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo productos activos y con stock disponible
        self.fields['producto'].queryset = Producto.objects.filter(
            activo=True,
            cantidad_disponible__gt=0
        )
        
        # Si hay un producto seleccionado, establecer su precio
        if self.instance and self.instance.producto:
            self.fields['precio_unitario'].initial = self.instance.producto.precio_base
    
    def clean(self):
        """
        Validaciones del formulario (Historia #21)
        """
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        cantidad = cleaned_data.get('cantidad')
        
        if producto and cantidad:
            # Validar que haya suficiente stock disponible
            if cantidad > producto.cantidad_disponible:
                raise forms.ValidationError(
                    f'Stock insuficiente para {producto.nombre}. '
                    f'Disponible: {producto.cantidad_disponible} {producto.get_unidad_medida_display()}'
                )
            
            # Validar que la cantidad sea positiva
            if cantidad <= 0:
                raise forms.ValidationError('La cantidad debe ser mayor a cero.')
            
            # Establecer el precio unitario del producto si no está definido
            if not cleaned_data.get('precio_unitario'):
                cleaned_data['precio_unitario'] = producto.precio_base
        
        return cleaned_data


# Formset para manejar múltiples productos en una venta
DetalleVentaFormSet = inlineformset_factory(
    Venta,
    DetalleVenta,
    form=DetalleVentaForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


class BuscarVentaForm(forms.Form):
    """
    Formulario de búsqueda de ventas (Historia #11, #19)
    """
    fecha_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'Fecha inicio'
        }),
        label='Desde'
    )
    
    fecha_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'Fecha fin'
        }),
        label='Hasta'
    )
    
    estado = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos los estados')] + Venta.ESTADO_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Estado'
    )
    
    buscar = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por ID de venta...'
        }),
        label='ID de Venta'
    )
    
    def clean(self):
        """Validar que la fecha de inicio no sea posterior a la fecha fin"""
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        
        if fecha_inicio and fecha_fin:
            if fecha_inicio > fecha_fin:
                raise forms.ValidationError(
                    'La fecha de inicio no puede ser posterior a la fecha fin.'
                )
        
        return cleaned_data


class CancelarVentaForm(forms.Form):
    """
    Formulario para cancelar una venta (Historia #12)
    """
    motivo = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese el motivo de la cancelación',
            'rows': 3
        }),
        label='Motivo de Cancelación'
    )
    
    def clean_motivo(self):
        """Validar que el motivo tenga al menos 10 caracteres"""
        motivo = self.cleaned_data.get('motivo')
        if motivo and len(motivo) < 10:
            raise forms.ValidationError('El motivo debe tener al menos 10 caracteres.')
        return motivo
