from django import forms
from .models import Proveedor

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        # Añadimos 'tipo_persona' al inicio de la lista
        fields = ['tipo_persona', 'nit', 'nombre_contacto', 'correo', 'telefono', 'direccion', 'departamento', 'ciudad', 'estado']
        
        # Aplicamos estilos de Bootstrap 5 a cada campo
        widgets = {
            'tipo_persona': forms.Select(attrs={
                'class': 'form-select', 
                'id': 'id_tipo_persona'  # ID clave para el script de JS
            }),
            'nit': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ingrese el número de identificación'
            }),
            'nombre_contacto': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Nombre completo'
            }),
            'correo': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'ejemplo@correo.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ej: 3101234567'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Calle/Carrera...'
            }),
            'departamento': forms.HiddenInput(),
            'ciudad': forms.HiddenInput(),
            'estado': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(ProveedorForm, self).__init__(*args, **kwargs)
        # Esto asegura que el label del NIT sea genérico por defecto
        self.fields['nit'].label = "Identificación"
        self.fields['telefono'].required = True
        self.fields['telefono'].error_messages.update({
            'required': 'El teléfono es obligatorio.'
        })

    def clean_telefono(self):
        telefono = (self.cleaned_data.get('telefono') or '').strip()

        if not telefono:
            raise forms.ValidationError('El teléfono es obligatorio.')

        qs = Proveedor.objects.filter(telefono=telefono)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError('Este teléfono ya está registrado.')

        return telefono