# Generated by Django 2.0 on 2018-04-21 17:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photo', '0023_filename_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imagefile',
            name='stem',
            field=models.CharField(
                max_length=1024, verbose_name='file name stem'
            ),
        ),
    ]
