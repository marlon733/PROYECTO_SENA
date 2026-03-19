# Generated migration for CopiaSeguridadBD model

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CopiaSeguridadBD',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255, verbose_name='Nombre de la Copia')),
                ('descripcion', models.TextField(blank=True, null=True, verbose_name='Descripción')),
                ('datos_backup', models.JSONField(default=dict, verbose_name='Datos de la Copia')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')),
                ('fecha_restauracion', models.DateTimeField(blank=True, null=True, verbose_name='Última Restauración')),
                ('tamaño_estimado', models.CharField(blank=True, max_length=50, verbose_name='Tamaño Estimado')),
            ],
            options={
                'verbose_name': 'Copia de Seguridad',
                'verbose_name_plural': 'Copias de Seguridad',
                'ordering': ['-fecha_creacion'],
            },
        ),
    ]
