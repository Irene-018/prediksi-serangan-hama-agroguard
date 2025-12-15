from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_sensordata'),
    ]

    operations = [
        migrations.AddField(
            model_name='lahan',
            name='foto_unit',
            field=models.ImageField(
                upload_to='lahan/',
                blank=True,
                null=True,
                verbose_name='Foto Unit Monitoring',
            ),
        ),
    ]


