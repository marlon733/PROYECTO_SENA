from django.db import models
from django.utils import timezone


class CopiaSeguridadBD(models.Model):
    """
    Modelo para almacenar copias de seguridad de la base de datos
    sin guardar archivos, todo en la BD como JSON
    """
    nombre = models.CharField(
        max_length=255,
        verbose_name='Nombre de la Copia'
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción'
    )
    datos_backup = models.JSONField(
        verbose_name='Datos de la Copia',
        default=dict
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    fecha_restauracion = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Última Restauración'
    )
    tamaño_estimado = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Tamaño Estimado'
    )
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Copia de Seguridad'
        verbose_name_plural = 'Copias de Seguridad'
    
    def __str__(self):
        return f"{self.nombre} - {self.fecha_creacion.strftime('%Y-%m-%d %H:%M')}"
