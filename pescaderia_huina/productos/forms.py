from django import forms
from .models import Producto

class ProductoForm(forms.ModelForm):

    class Meta:
        model = Producto
        fields = [
            "proveedor",  # <--- NUEVO: Campo obligatorio
            "tipo_producto",
            "nombre",
            "descripcion",
            "tipo_presentacion",
            "precio",
            "estado",
            # NOTA: No incluimos 'stock' para que siempre inicie en 0
        ]

        widgets = {
            # Estilo para el selector de proveedor
            "proveedor": forms.Select(attrs={
                "class": "form-select", 
                "data-placeholder": "Seleccione un proveedor..."
            }),
            
            "tipo_producto": forms.Select(attrs={"class": "form-select"}),
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Trucha Arcoíris"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Detalles del producto..."}),
            "tipo_presentacion": forms.Select(attrs={"class": "form-select"}),
            "precio": forms.NumberInput(attrs={"class": "form-control", "placeholder": "0.00"}),
            "estado": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        
    # Opcional: Personalizar las etiquetas si quieres que se vean diferente al modelo
    def _init_(self, *args, **kwargs):
        super(ProductoForm, self)._init_(*args, **kwargs)
        # Esto hace que el dropdown de proveedores tenga una opción vacía al inicio
        self.fields['proveedor'].empty_label = "Seleccione un Proveedor..."
