# Generated by Django 4.1 on 2022-09-02 06:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_segmentation', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='name',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
