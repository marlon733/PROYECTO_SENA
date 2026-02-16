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
    class Meta:
        model = DetallePedido
        fields = ['producto', 'cantidad', 'precio_unitario']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad <= 0:
            raise forms.ValidationError("La cantidad debe ser mayor a cero.")
        return cantidad