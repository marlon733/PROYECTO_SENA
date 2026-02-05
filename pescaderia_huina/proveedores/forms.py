from django import forms
from .models import Proveedor

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        # Incluimos los campos que el usuario debe llenar
        fields = ['nit', 'nombre_contacto', 'correo', 'telefono', 'direccion', 'ciudad', 'estado']
        
        # Aplicamos estilos de Bootstrap 5 a cada campo
        widgets = {
            'nit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 900.123.456-1'}),
            'nombre_contacto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@correo.com'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 3101234567'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Calle/Carrera...'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ciudad de origen'}),
            'estado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }