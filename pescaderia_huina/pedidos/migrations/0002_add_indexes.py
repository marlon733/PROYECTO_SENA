# Generated migration - Agregar índices de performance

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pedidos', '0001_initial'),
    ]

    operations = [
        # Índice para búsquedas por proveedor y estado (más común)
        migrations.AddIndex(
            model_name='pedido',
            index=models.Index(
                fields=['proveedor', 'estado'],
                name='pedidos_proveedor_estado_idx',
            ),
        ),
        # Índice para ordenamiento por fecha (listados)
        migrations.AddIndex(
            model_name='pedido',
            index=models.Index(
                fields=['-fecha'],
                name='pedidos_fecha_desc_idx',
            ),
        ),
        # Índice para filtrado por estado
        migrations.AddIndex(
            model_name='pedido',
            index=models.Index(
                fields=['estado'],
                name='pedidos_estado_idx',
            ),
        ),
        # Índice para joins con DetallePedido
        migrations.AddIndex(
            model_name='detallepedido',
            index=models.Index(
                fields=['pedido', 'producto'],
                name='detallepedido_pedido_producto_idx',
            ),
        ),
    ]
