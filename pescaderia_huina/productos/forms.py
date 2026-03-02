from django import forms
from django.db.models import Q
from .models import Producto
from proveedores.models import Proveedor 

# Formulario 1: Solo para seleccionar el PROVEEDOR (Cabecera)
class ProveedorSelectForm(forms.Form):
    proveedor = forms.ModelChoiceField(
        queryset=Proveedor.objects.filter(estado=True).order_by('nombre_contacto'),
        empty_label="Seleccione el Proveedor...",
        widget=forms.Select(attrs={'class': 'form-select form-select-lg fw-bold border-primary'})
    )

# Formulario 2: Para cada FILA de producto (Sin proveedor, sin stock)
class ProductoItemForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            "tipo_producto",
            "nombre",
            "descripcion",
            "tipo_presentacion",
            "precio",
            "estado",
        ]
        widgets = {
            "tipo_producto": forms.Select(attrs={"class": "form-select form-select-sm"}),
            "nombre": forms.TextInput(attrs={"class": "form-control form-control-sm", "placeholder": "Nombre del producto"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control form-control-sm", "rows": 1, "placeholder": "Detalles..."}),
            "tipo_presentacion": forms.Select(attrs={"class": "form-select form-select-sm"}),
            "precio": forms.NumberInput(attrs={"class": "form-control form-control-sm", "placeholder": "0.00"}),
            "estado": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

        
    # Opcional: Personalizar las etiquetas si quieres que se vean diferente al modelo
    def _init_(self, *args, **kwargs):
        super(ProductoForm, self)._init_(*args, **kwargs)
        # Esto hace que el dropdown de proveedores tenga una opción vacía al inicio
        self.fields['proveedor'].empty_label = "Seleccione un Proveedor..."


# Mantenemos tu formulario original para la edición individual
class ProductoForm(forms.ModelForm):
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
            "precio": forms.NumberInput(attrs={"class": "form-control"}),
            "estado": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
    
    def __init__(self, *args, **kwargs):
        super(ProductoForm, self).__init__(*args, **kwargs)
        self.fields['proveedor'].empty_label = "Seleccione un Proveedor..."
        consulta = Q(estado=True)
        if self.instance.pk and self.instance.proveedor:
            consulta = consulta | Q(id=self.instance.proveedor.id)
        self.fields['proveedor'].queryset = Proveedor.objects.filter(consulta).order_by('nombre_contacto')

