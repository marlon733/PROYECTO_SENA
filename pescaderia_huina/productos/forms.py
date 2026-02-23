from django import forms
from .models import Producto


class ProductoForm(forms.ModelForm):

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
            "tipo_producto": forms.Select(attrs={"class": "form-select"}),
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "tipo_presentacion": forms.Select(attrs={"class": "form-select", "id": "tipo_presentacion"}),
           
            "precio": forms.NumberInput(attrs={"class": "form-control"}),
            "estado": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

   