from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pedidos', '0002_add_indexes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='detallepedido',
            name='producto',
            field=models.ForeignKey(on_delete=models.PROTECT, to='productos.producto'),
        ),
    ]
