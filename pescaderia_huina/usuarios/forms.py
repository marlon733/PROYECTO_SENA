from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django_recaptcha.fields import ReCaptchaField
from datetime import date
from .models import PerfilUsuario


ROL_ADMIN = 'admin'
ROL_EMPLEADO = 'empleado'
ROL_CHOICES = (
    (ROL_ADMIN, 'Administrador'),
    (ROL_EMPLEADO, 'Empleado'),
)

ALLOWED_PROFILE_MEDIA_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.mp4', '.webm', '.mov', '.m4v'}
MAX_PROFILE_MEDIA_SIZE = 25 * 1024 * 1024  # 25MB


def _max_birth_date_for_min_age(min_age=15):
    """Retorna la fecha máxima de nacimiento permitida para cumplir edad mínima."""
    today = date.today()
    try:
        return today.replace(year=today.year - min_age)
    except ValueError:
        # Ajuste para fechas como 29/02 en años no bisiestos.
        return today.replace(year=today.year - min_age, day=28)


def _clean_telefono_value(raw_value):
    """Normaliza y valida que el telefono contenga solo digitos."""
    telefono = (raw_value or '').strip()
    if not telefono:
        return telefono

    if not telefono.isdigit():
        raise ValidationError('El teléfono debe contener solo números.')

    if not (7 <= len(telefono) <= 15):
        raise ValidationError('El teléfono debe tener entre 7 y 15 dígitos.')

    return telefono


def _clean_profile_photo(uploaded_file):
    """Valida tamaño y extensión de archivo de perfil (imagen/video)."""
    if not uploaded_file:
        return uploaded_file

    import os

    extension = os.path.splitext(uploaded_file.name)[1].lower()
    if extension not in ALLOWED_PROFILE_MEDIA_EXTENSIONS:
        raise ValidationError('Formato no permitido. Usa JPG, PNG, WEBP, GIF, MP4, WEBM o MOV.')

    if uploaded_file.size > MAX_PROFILE_MEDIA_SIZE:
        raise ValidationError('El archivo de perfil no puede superar 25MB.')

    return uploaded_file

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
            'placeholder': 'Teléfono (opcional)',
            'inputmode': 'numeric',
            'pattern': r'\d{7,15}',
            'maxlength': '15',
            'autocomplete': 'tel'
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

    foto_perfil = forms.FileField(
        required=False,
        label='Foto o video de perfil',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*,video/*'
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

    def clean_telefono(self):
        return _clean_telefono_value(self.cleaned_data.get('telefono'))

    def clean_foto_perfil(self):
        return _clean_profile_photo(self.cleaned_data.get('foto_perfil'))

    def __init__(self, *args, actor_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.actor_user = actor_user

        # Restringe el calendario para impedir seleccionar menores de 15 años.
        max_birth_date = _max_birth_date_for_min_age(15)
        self.fields['fecha_nacimiento'].widget.attrs['max'] = max_birth_date.isoformat()

        # Por seguridad: solo un administrador (staff) puede elegir/crear admins.
        can_choose_role = bool(actor_user and getattr(actor_user, 'is_authenticated', False) and actor_user.is_staff)
        if not can_choose_role:
            self.fields['rol'].initial = ROL_EMPLEADO
            self.fields['rol'].disabled = True
            self.fields['rol'].help_text = 'Solo un administrador puede asignar rol.'

    def clean_fecha_nacimiento(self):
        fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        if not fecha_nacimiento:
            return fecha_nacimiento

        max_birth_date = _max_birth_date_for_min_age(15)
        if fecha_nacimiento > max_birth_date:
            raise forms.ValidationError('Debes tener al menos 15 años para registrarte.')

        return fecha_nacimiento
    
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
            if self.cleaned_data.get('foto_perfil'):
                perfil.foto_perfil = self.cleaned_data.get('foto_perfil')
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
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'inputmode': 'numeric',
                'pattern': r'\d{7,15}',
                'maxlength': '15',
                'autocomplete': 'tel'
            }),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'foto_perfil': forms.FileInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        max_birth_date = _max_birth_date_for_min_age(15)
        self.fields['fecha_nacimiento'].widget.attrs['max'] = max_birth_date.isoformat()

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

    def clean_telefono(self):
        return _clean_telefono_value(self.cleaned_data.get('telefono'))

    def clean_fecha_nacimiento(self):
        fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        if not fecha_nacimiento:
            return fecha_nacimiento

        max_birth_date = _max_birth_date_for_min_age(15)
        if fecha_nacimiento > max_birth_date:
            raise forms.ValidationError('Debes tener al menos 15 años.')

        return fecha_nacimiento

    def clean_foto_perfil(self):
        return _clean_profile_photo(self.cleaned_data.get('foto_perfil'))


class EditarMiPerfilForm(forms.ModelForm):
    """Formulario para que el usuario edite su perfil (sin documento)."""

    class Meta:
        model = PerfilUsuario
        fields = ['telefono', 'direccion', 'foto_perfil', 'fecha_nacimiento']
        widgets = {
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'inputmode': 'numeric',
                'pattern': r'\d{7,15}',
                'maxlength': '15',
                'autocomplete': 'tel'
            }),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'foto_perfil': forms.FileInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        max_birth_date = _max_birth_date_for_min_age(15)
        self.fields['fecha_nacimiento'].widget.attrs['max'] = max_birth_date.isoformat()

    def clean_telefono(self):
        return _clean_telefono_value(self.cleaned_data.get('telefono'))

    def clean_fecha_nacimiento(self):
        fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        if not fecha_nacimiento:
            return fecha_nacimiento

        max_birth_date = _max_birth_date_for_min_age(15)
        if fecha_nacimiento > max_birth_date:
            raise forms.ValidationError('Debes tener al menos 15 años.')

        return fecha_nacimiento

    def clean_foto_perfil(self):
        return _clean_profile_photo(self.cleaned_data.get('foto_perfil'))