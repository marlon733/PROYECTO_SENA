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

    def clean(self):
        cleaned_data = super().clean()
        tipo_presentacion = cleaned_data.get("tipo_presentacion")
        peso = cleaned_data.get("peso")

        if tipo_presentacion == "LIB" and peso and peso <= 0:
            raise forms.ValidationError("El peso en libras debe ser mayor a 0.")

        if tipo_presentacion in ["VAC", "BAN"] and peso and peso <= 0:
            raise forms.ValidationError("La cantidad en unidades debe ser mayor a 0.")

        return cleaned_data
