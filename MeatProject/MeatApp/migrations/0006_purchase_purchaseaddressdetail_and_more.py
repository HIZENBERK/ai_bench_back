# Generated by Django 5.0.4 on 2024-08-27 08:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MeatApp', '0005_alter_product_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase',
            name='PurchaseAddressDetail',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='purchase',
            name='Purchaser',
            field=models.CharField(max_length=100),
        ),
    ]
