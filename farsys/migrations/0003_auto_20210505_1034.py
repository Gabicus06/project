# Generated by Django 3.2 on 2021-05-05 15:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('farsys', '0002_auto_20210504_1932'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='categoria',
            new_name='category',
        ),
        migrations.RemoveField(
            model_name='product',
            name='box_units',
        ),
        migrations.RemoveField(
            model_name='product',
            name='nombre',
        ),
        migrations.RemoveField(
            model_name='product',
            name='presentacion',
        ),
        migrations.RemoveField(
            model_name='product',
            name='price_box',
        ),
        migrations.RemoveField(
            model_name='product',
            name='price_tira',
        ),
        migrations.RemoveField(
            model_name='product',
            name='price_unit',
        ),
        migrations.RemoveField(
            model_name='product',
            name='stock',
        ),
        migrations.RemoveField(
            model_name='product',
            name='tira_units',
        ),
        migrations.AddField(
            model_name='product',
            name='name',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price_1', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=6, null=True)),
                ('price_2', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=6, null=True)),
                ('price_3', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=6, null=True)),
                ('unit_1', models.IntegerField(blank=True, default=1, null=True)),
                ('unit_2', models.IntegerField(blank=True, default=0, null=True)),
                ('unit_3', models.IntegerField(blank=True, default=0, null=True)),
                ('stock', models.IntegerField(blank=True, default=0, null=True)),
                ('obs', models.CharField(blank=True, max_length=50, null=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='farsys.account')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='farsys.product')),
            ],
        ),
    ]
