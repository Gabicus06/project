# Generated by Django 3.2 on 2021-05-20 19:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('farsys', '0007_remove_product_editable'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='editable',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
