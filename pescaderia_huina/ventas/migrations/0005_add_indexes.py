# Generated migration - Agregar índices de performance

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0004_venta_iva_monto_venta_subtotal_alter_venta_cantidad_and_more'),
    ]

    operations = [
        # Índice para búsquedas por estado
        migrations.AddIndex(
            model_name='venta',
            index=models.Index(
                fields=['estado'],
                name='ventas_estado_idx',
            ),
        ),
        # Índice para ordenamiento por fecha (listados)
        migrations.AddIndex(
            model_name='venta',
            index=models.Index(
                fields=['-fecha_venta'],
                name='ventas_fecha_venta_desc_idx',
            ),
        ),
        # Índice para búsquedas por cliente
        migrations.AddIndex(
            model_name='venta',
            index=models.Index(
                fields=['nombre_cliente'],
                name='ventas_nombre_cliente_idx',
            ),
        ),
        # Índice para joins con VentaItem
        migrations.AddIndex(
            model_name='ventaitem',
            index=models.Index(
                fields=['venta', 'producto'],
                name='ventaitem_venta_producto_idx',
            ),
        ),
    ]
