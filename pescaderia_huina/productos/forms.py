from django import forms
from django.db.models import Q
from .models import Producto
from proveedores.models import Proveedor 

# Formulario 1: Solo para seleccionar el PROVEEDOR (Cabecera)
class ProveedorSelectForm(forms.Form):
    proveedor = forms.ModelChoiceField(
        queryset=Proveedor.objects.filter(estado=True).order_by('nombre_contacto'),
        empty_label="Seleccione el Proveedor...",
        widget=forms.Select(attrs={'class': 'form-select form-select-lg fw-bold border-primary'}),
        required=True
    )

# Formulario 2: Para cada FILA de producto (Sin proveedor, sin stock)
class ProductoItemForm(forms.ModelForm):
    precio = forms.DecimalField(
        max_digits=10,
        decimal_places=0,
        min_value=0,
        widget=forms.NumberInput(attrs={
            "class": "form-control form-control-sm",
            "placeholder": "0",
            "step": "1",
            "min": "0"
        })
    )

    class Meta:
        model = Producto
        fields = [
            "tipo_producto",
            "nombre",
            "tipo_presentacion",
            "precio",
            "estado",
        ]
        widgets = {
            "tipo_producto": forms.Select(attrs={"class": "form-select form-select-sm"}),
            "nombre": forms.TextInput(attrs={"class": "form-control form-control-sm", "placeholder": "Nombre del producto"}),
            "tipo_presentacion": forms.Select(attrs={"class": "form-select form-select-sm"}),
            "estado": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super(ProductoItemForm, self).__init__(*args, **kwargs)
        # Asegurar que los campos requeridos sean validados
        self.fields['tipo_producto'].required = True
        self.fields['nombre'].required = True
        self.fields['tipo_presentacion'].required = True
        self.fields['precio'].required = True
        self.fields['estado'].required = False


# Mantenemos tu formulario original para la edición individual
class ProductoForm(forms.ModelForm):
    precio = forms.DecimalField(
        max_digits=10,
        decimal_places=0,
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "1", "min": "0", "placeholder": "0"})
    )

    # ... (Tu código anterior del ProductoForm se queda igual) ...
    class Meta:
        model = Producto
        fields = ["proveedor", "tipo_producto", "nombre", "descripcion", "tipo_presentacion", "precio", "estado"]
        widgets = {
            "proveedor": forms.Select(attrs={"class": "form-select"}),
            "tipo_producto": forms.Select(attrs={"class": "form-select"}),
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "tipo_presentacion": forms.Select(attrs={"class": "form-select"}),
            "estado": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
    
    def __init__(self, *args, **kwargs):
        super(ProductoForm, self).__init__(*args, **kwargs)
        self.fields['proveedor'].empty_label = "Seleccione un Proveedor..."
        consulta = Q(estado=True)
        if self.instance.pk and self.instance.proveedor:
            consulta = consulta | Q(id=self.instance.proveedor.id)
        self.fields['proveedor'].queryset = Proveedor.objects.filter(consulta).order_by('nombre_contacto')

