from django.contrib import admin
from .models import CopiaSeguridadBD


@admin.register(CopiaSeguridadBD)
class CopiaSeguridadBDAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha_creacion', 'fecha_restauracion', 'tamaño_estimado')
    list_filter = ('fecha_creacion', 'fecha_restauracion')
    search_fields = ('nombre', 'descripcion')
    readonly_fields = ('fecha_creacion', 'fecha_restauracion', 'datos_backup')
    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'descripcion', 'tamaño_estimado')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_restauracion')
        }),
        ('Datos', {
            'fields': ('datos_backup',),
            'classes': ('collapse',)
        }),
    )
