

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from uuid import uuid4


def perfil_photo_upload_to(instance, filename):
    """Genera rutas estables y nombres unicos para archivos de perfil."""
    import os

    extension = os.path.splitext(filename)[1].lower() or '.jpg'
    user_id = instance.user_id or 'anon'
    return f'perfil/user_{user_id}/{uuid4().hex}{extension}'

class PerfilUsuario(models.Model):
    """
    Modelo para extender la información del usuario
    Relacionado 1:1 con el modelo User de Django
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='perfil'
    )
    recovery_code = models.CharField(
        max_length=6,
        blank=True,
        null=True
    )
    recovery_code_created = models.DateTimeField(
        blank=True,
        null=True
    )
    def __str__(self):
        return self.user.username
    documento = models.CharField(
        max_length=20, 
        unique=True,
        blank=True,
        null=True,
        help_text="Número de documento de identidad"
    )
    
    telefono = models.CharField(
        max_length=15, 
        blank=True,
        help_text="Número de teléfono"
    )
    
    direccion = models.CharField(
        max_length=200, 
        blank=True,
        help_text="Dirección de residencia"
    )
    
    foto_perfil = models.FileField(
        upload_to=perfil_photo_upload_to,
        blank=True, 
        null=True,
        help_text="Archivo de perfil (imagen o video)"
    )
    
    fecha_nacimiento = models.DateField(
        null=True, 
        blank=True,
        help_text="Fecha de nacimiento"
    )
    
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"
        ordering = ['-user__date_joined']
    
    def __str__(self):
        return f"Perfil de {self.user.username}"
    
    def get_nombre_completo(self):
        """Retorna el nombre completo del usuario"""
        return f"{self.user.first_name} {self.user.last_name}"
    
    def get_rol(self):
        """Retorna el rol del usuario: 'Administrador' o 'Empleado'"""
        return 'Administrador' if self.user.is_staff else 'Empleado'

    @property
    def perfil_media_extension(self):
        if not self.foto_perfil:
            return ''
        import os
        return os.path.splitext(self.foto_perfil.name)[1].lower()

    @property
    def es_imagen_perfil(self):
        return self.perfil_media_extension in {'.jpg', '.jpeg', '.png', '.webp', '.gif'}

    @property
    def es_video_perfil(self):
        return self.perfil_media_extension in {'.mp4', '.webm', '.mov', '.m4v'}


# Señales para crear/actualizar perfil automáticamente
@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """
    Crea automáticamente un perfil cuando se crea un usuario
    """
    if created:
        try:
            PerfilUsuario.objects.create(user=instance)
        except Exception as e:
            print(f"Error creando perfil para {instance.username}: {e}")

@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    """
    Guarda el perfil cuando se guarda el usuario
    """
    if hasattr(instance, 'perfil'):
        try:
            instance.perfil.save()
        except Exception as e:
            print(f"Error guardando perfil de {instance.username}: {e}")
        
