from django import forms
from .models import Pedido, DetallePedido, Proveedor    
from productos.models import Producto
from proveedores.models import Proveedor


class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        # El ID se genera solo, la fecha es auto_now_add y el valor_total lo calculamos
        fields = ['proveedor', 'estado']
        widgets = {
            'proveedor': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

class DetallePedidoForm(forms.ModelForm):
    OPCIONES_PRESENTACION = [
        ('unidades', 'Uds'),
        ('bandejas', 'Band'),
        ('libras', 'Lib'),
    ]

    presentacion = forms.ChoiceField(
        choices=OPCIONES_PRESENTACION,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select bg-light unidad-select',
            'style': 'max-width: 95px; border-left: 1px solid #dce9f9;'
        })
    )

    # 1. FORZAMOS A DJANGO A ENTENDER LA COMA COMO DECIMAL
    cantidad = forms.DecimalField(
        localize=True, 
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 
            'min': '0', 
            'step': 'any' # 'any' permite que el navegador acepte cualquier número decimal
        })
    )

    class Meta:
        model = DetallePedido
        fields = ['producto', 'cantidad', 'presentacion', 'precio_unitario'] 
        
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': 'any'}),
        }
    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad <= 0:
            raise forms.ValidationError("La cantidad debe ser mayor a cero.")
        return cantidad