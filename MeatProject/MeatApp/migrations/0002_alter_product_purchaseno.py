# Generated by Django 5.0.4 on 2024-06-09 21:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MeatApp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='PurchaseNo',
            field=models.ForeignKey(blank=True, db_column='PurchaseNo', null=True, on_delete=django.db.models.deletion.SET_NULL, to='MeatApp.purchase', to_field='PurchaseNo'),
        ),
    ]
