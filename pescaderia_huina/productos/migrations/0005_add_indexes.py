# Generated migration - Agregar índices de performance

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0004_remove_peso_field'),
    ]

    operations = [
        # Índice para búsquedas por nombre
        migrations.AddIndex(
            model_name='producto',
            index=models.Index(
                fields=['nombre'],
                name='productos_nombre_idx',
            ),
        ),
        # Índice para filtrado por tipo
        migrations.AddIndex(
            model_name='producto',
            index=models.Index(
                fields=['tipo_producto'],
                name='productos_tipo_idx',
            ),
        ),
        # Índice para filtrado por estado y tipo (listados activos)
        migrations.AddIndex(
            model_name='producto',
            index=models.Index(
                fields=['estado', 'tipo_producto'],
                name='productos_estado_tipo_idx',
            ),
        ),
        # Índice para joins con proveedor
        migrations.AddIndex(
            model_name='producto',
            index=models.Index(
                fields=['proveedor'],
                name='productos_proveedor_idx',
            ),
        ),
    ]
