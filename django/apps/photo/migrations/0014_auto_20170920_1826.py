# Generated by Django 1.11 on 2017-09-20 16:26

import django.core.validators
from django.db import migrations
import sorl.thumbnail.fields

import apps.photo.models


class Migration(migrations.Migration):

    dependencies = [
        ('photo', '0013_imagefile_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imagefile',
            name='source_file',
            field=sorl.thumbnail.fields.ImageField(
                height_field='full_height',
                max_length=1024,
                upload_to=apps.photo.models.upload_image_to,
                validators=[
                    django.core.validators.FileExtensionValidator([
                        'jpg', 'jpeg', 'png'
                    ])
                ],
                verbose_name='source file',
                width_field='full_width'
            ),
        ),
    ]