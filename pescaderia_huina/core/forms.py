from django import forms
from productos.models import Producto


class BusquedaProductoForm(forms.Form):
    """Formulario para buscar y filtrar productos por tipo o nombre"""
    tipo_producto = forms.ChoiceField(
        required=False,
        label='Categoría',
        choices=[('', 'Todas')] + Producto.TIPO_PRODUCTO,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    buscar = forms.CharField(
        required=False,
        label='Buscar',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre del producto...'
        })
    )
