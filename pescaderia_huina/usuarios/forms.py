from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django_recaptcha.fields import ReCaptchaField
from .models import PerfilUsuario


ROL_ADMIN = 'admin'
ROL_EMPLEADO = 'empleado'
ROL_CHOICES = (
    (ROL_ADMIN, 'Administrador'),
    (ROL_EMPLEADO, 'Empleado'),
)

class LoginForm(AuthenticationForm):
    """
    Formulario personalizado para inicio de sesión
    Usamos el campo username para almacenar el documento
    """
    username = forms.CharField(
        label='Documento',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su documento',
            'autofocus': True,
            'inputmode': 'numeric',
            'pattern': r'\d{8,10}',
            'minlength': '8',
            'maxlength': '10',
            'autocomplete': 'off'
        })
    )
    
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su contraseña'
        })
    )
    
    remember_me = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Recordarme'
    )
    
    captcha = ReCaptchaField(
        label='Verificación de Seguridad'
    )

    def clean_username(self):
        documento = (self.cleaned_data.get('username') or '').strip()
        if not documento.isdigit():
            raise forms.ValidationError('El documento debe contener solo números.')
        if not (8 <= len(documento) <= 10):
            raise forms.ValidationError('El documento debe tener entre 8 y 10 dígitos.')
        return documento


class RegistroForm(UserCreationForm):
    """
    Formulario para registro de nuevos usuarios
    Extiende UserCreationForm de Django
    """
    documento = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número de documento',
            'inputmode': 'numeric',
            'pattern': r'\d{8,10}',
            'minlength': '8',
            'maxlength': '10',
            'autocomplete': 'off'
        })
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        })
    )
    
    first_name = forms.CharField(
        max_length=150,
        required=True,
        label='Nombre',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre'
        })
    )
    
    last_name = forms.CharField(
        max_length=150,
        required=True,
        label='Apellido',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido'
        })
    )
    
    telefono = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Teléfono (opcional)'
        })
    )

    direccion = forms.CharField(
        max_length=255,
        required=False,
        label='Dirección',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Dirección (opcional)'
        })
    )

    fecha_nacimiento = forms.DateField(
        required=False,
        label='Fecha de nacimiento',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    rol = forms.ChoiceField(
        choices=ROL_CHOICES,
        required=True,
        label='Tipo de usuario',
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )

    # Campo interno para compatibilidad con UserCreationForm.
    username = forms.CharField(required=False, widget=forms.HiddenInput())
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }
    
    def clean_documento(self):
        """Valida que el documento no exista y cumpla formato (8-10 dígitos numéricos)."""
        documento = (self.cleaned_data.get('documento') or '').strip()

        if not documento.isdigit():
            raise forms.ValidationError('El documento debe contener solo números.')

        if not (8 <= len(documento) <= 10):
            raise forms.ValidationError('El documento debe tener entre 8 y 10 dígitos.')

        if PerfilUsuario.objects.filter(documento=documento).exists():
            raise forms.ValidationError('Este documento ya está registrado.')

        if User.objects.filter(username=documento).exists():
            raise forms.ValidationError('Este documento ya está registrado como usuario.')

        return documento

    def clean_username(self):
        # UserCreationForm valida este campo; se deriva desde `documento`.
        return (self.cleaned_data.get('documento') or '').strip()
    
    def clean_email(self):
        """Valida que el email no exista en la base de datos"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado.')
        return email

    def __init__(self, *args, actor_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.actor_user = actor_user

        # Por seguridad: solo un administrador (staff) puede elegir/crear admins.
        can_choose_role = bool(actor_user and getattr(actor_user, 'is_authenticated', False) and actor_user.is_staff)
        if not can_choose_role:
            self.fields['rol'].initial = ROL_EMPLEADO
            self.fields['rol'].disabled = True
            self.fields['rol'].help_text = 'Solo un administrador puede asignar rol.'
    
    def save(self, commit=True):
        """
        Guarda el usuario y crea su perfil con el documento
        """
        user = super().save(commit=False)
        user.username = (self.cleaned_data.get('documento') or '').strip()  # Usamos documento como username
        user.email = self.cleaned_data['email']

        # Rol (admin/empleado) — solo lo puede definir un actor staff.
        # Si el campo está deshabilitado, Django no lo incluye en cleaned_data,
        # así que usamos el initial value que establecimos en __init__
        rol = (self.cleaned_data.get('rol') or 
               self.fields['rol'].initial or 
               ROL_EMPLEADO)
        
        can_assign_staff = bool(self.actor_user and getattr(self.actor_user, 'is_authenticated', False) and self.actor_user.is_staff)
        user.is_staff = (rol == ROL_ADMIN) if can_assign_staff else False
        
        if commit:
            user.save()
            # El perfil se crea automáticamente por la señal
            perfil = user.perfil
            perfil.documento = (self.cleaned_data.get('documento') or '').strip()
            perfil.telefono = self.cleaned_data.get('telefono', '')
            perfil.direccion = self.cleaned_data.get('direccion', '')
            perfil.fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
            perfil.save()
        
        return user


class EditarUsuarioForm(forms.ModelForm):
    """
    Formulario para editar información del usuario
    """

    rol = forms.ChoiceField(
        choices=ROL_CHOICES,
        required=True,
        label='Tipo de usuario',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'is_active']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo Electrónico',
            'is_active': 'Usuario Activo',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance is not None:
            self.fields['rol'].initial = ROL_ADMIN if instance.is_staff else ROL_EMPLEADO
            if instance.is_superuser:
                self.fields['rol'].disabled = True
                self.fields['rol'].help_text = 'El rol de un superusuario no se puede modificar.'

    def save(self, commit=True):
        user = super().save(commit=False)
        if not getattr(user, 'is_superuser', False):
            rol = self.cleaned_data.get('rol') or ROL_EMPLEADO
            user.is_staff = (rol == ROL_ADMIN)
        if commit:
            user.save()
        return user


class EditarUsuarioPerfilAdminForm(forms.ModelForm):
    """Edición de perfil por admin (sin flags extras como is_active).

    Se usa en la vista `editar_perfil_view` cuando el admin edita a otro usuario,
    para exponer un desplegable de rol sin introducir campos no renderizados.
    """

    rol = forms.ChoiceField(
        choices=ROL_CHOICES,
        required=True,
        label='Tipo de usuario',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo Electrónico',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance is not None:
            self.fields['rol'].initial = ROL_ADMIN if instance.is_staff else ROL_EMPLEADO
            if instance.is_superuser:
                self.fields['rol'].disabled = True
                self.fields['rol'].help_text = 'El rol de un superusuario no se puede modificar.'

    def save(self, commit=True):
        user = super().save(commit=False)
        if not getattr(user, 'is_superuser', False):
            rol = self.cleaned_data.get('rol') or ROL_EMPLEADO
            user.is_staff = (rol == ROL_ADMIN)
        if commit:
            user.save()
        return user


class EditarMiUsuarioForm(forms.ModelForm):
    """Formulario para que el usuario edite su propia información (sin flags admin)."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo Electrónico',
        }


class EditarPerfilForm(forms.ModelForm):
    """
    Formulario para editar el perfil del usuario
    """
    class Meta:
        model = PerfilUsuario
        fields = ['documento', 'telefono', 'direccion', 'foto_perfil', 'fecha_nacimiento']
        widgets = {
            'documento': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'foto_perfil': forms.FileInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def clean_documento(self):
        documento = (self.cleaned_data.get('documento') or '').strip()

        if not documento.isdigit():
            raise forms.ValidationError('El documento debe contener solo números.')
        if not (8 <= len(documento) <= 10):
            raise forms.ValidationError('El documento debe tener entre 8 y 10 dígitos.')

        qs = PerfilUsuario.objects.filter(documento=documento)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Este documento ya está registrado.')

        return documento


class EditarMiPerfilForm(forms.ModelForm):
    """Formulario para que el usuario edite su perfil (sin documento)."""

    class Meta:
        model = PerfilUsuario
        fields = ['telefono', 'direccion', 'foto_perfil', 'fecha_nacimiento']
        widgets = {
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'foto_perfil': forms.FileInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }