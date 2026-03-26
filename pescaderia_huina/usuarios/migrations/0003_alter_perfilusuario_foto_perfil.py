from django.db import migrations, models
import usuarios.models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0002_alter_perfilusuario_documento'),
    ]

    operations = [
        migrations.AlterField(
            model_name='perfilusuario',
            name='foto_perfil',
            field=models.FileField(blank=True, help_text='Archivo de perfil (imagen o video)', null=True, upload_to=usuarios.models.perfil_photo_upload_to),
        ),
    ]
