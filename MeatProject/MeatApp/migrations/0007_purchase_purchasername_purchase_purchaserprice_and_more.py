# Generated by Django 5.0.4 on 2024-08-30 04:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MeatApp', '0006_purchase_purchaseaddressdetail_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase',
            name='PurchaserName',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='purchase',
            name='PurchaserPrice',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='purchase',
            name='PurchaseAddressDetail',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='purchase',
            name='Wrapping',
            field=models.BooleanField(max_length=10),
        ),
    ]
