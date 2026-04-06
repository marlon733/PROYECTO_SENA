from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0005_add_indexes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ventaitem',
            name='producto',
            field=models.ForeignKey(on_delete=models.PROTECT, to='productos.producto', verbose_name='Producto'),
        ),
    ]
