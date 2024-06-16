# Generated by Django 5.0.4 on 2024-06-16 05:04

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('ClientType', models.CharField(max_length=100)),
                ('ClientName', models.CharField(max_length=100, unique=True)),
                ('RepresentativeName', models.CharField(max_length=100)),
                ('BusinessRegistrationNumber', models.CharField(max_length=100)),
                ('ClientAddress', models.CharField(max_length=100)),
                ('ClientPhone', models.CharField(max_length=100)),
                ('PersonInCharge', models.CharField(max_length=100)),
                ('PersonInChargePhone', models.CharField(max_length=100)),
                ('FirstTradeDate', models.DateField()),
                ('LastTradeDate', models.DateField()),
                ('Payment_Delivery', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='MeatPart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Part name')),
                ('code', models.CharField(blank=True, max_length=5, unique=True, verbose_name='Part code')),
            ],
        ),
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('PurchaseDate', models.DateTimeField(auto_now_add=True)),
                ('PurchaseStep', models.CharField(max_length=10)),
                ('PurchaseAddress', models.CharField(max_length=100)),
                ('PurchasePhone', models.CharField(max_length=15)),
                ('PurchaseNo', models.CharField(blank=True, max_length=10, unique=True)),
                ('Wrapping', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('OrderDate', models.DateField(auto_now=True)),
                ('ETA', models.DateField()),
                ('OrderWeight', models.IntegerField()),
                ('OrderPrice', models.IntegerField(default=0)),
                ('OrderNo', models.CharField(blank=True, max_length=100, unique=True)),
                ('OrderSituation', models.CharField(max_length=10)),
                ('addDateTime', models.DateTimeField(auto_now=True)),
                ('Client', models.ForeignKey(db_column='Client', on_delete=django.db.models.deletion.CASCADE, to='MeatApp.client', to_field='ClientName')),
                ('Part', models.ForeignKey(db_column='Part', on_delete=django.db.models.deletion.CASCADE, to='MeatApp.meatpart', to_field='code')),
            ],
            options={
                'ordering': ['-addDateTime'],
            },
        ),
        migrations.CreateModel(
            name='InOutCome',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('IncomePrice', models.IntegerField(default=0)),
                ('OutcomePrice', models.IntegerField(default=0)),
                ('IncomeAmount', models.IntegerField(default=0)),
                ('OutcomeAmount', models.IntegerField(default=0)),
                ('IncomeDate', models.DateField()),
                ('OutcomeDate', models.DateField()),
                ('Gifts', models.IntegerField(default=0)),
                ('Part', models.ForeignKey(db_column='Part', on_delete=django.db.models.deletion.CASCADE, to='MeatApp.order')),
            ],
        ),
        migrations.CreateModel(
            name='OtherCost',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('Category', models.CharField(max_length=100)),
                ('SubsidiaryMaterial', models.CharField(max_length=100)),
                ('Quntity', models.IntegerField(default=0)),
                ('Price', models.IntegerField(default=0)),
                ('TotalPrice', models.IntegerField(default=0)),
                ('CostSituation', models.CharField(max_length=100)),
                ('Client', models.ForeignKey(db_column='Client', on_delete=django.db.models.deletion.CASCADE, to='MeatApp.client', to_field='ClientName')),
            ],
        ),
        migrations.CreateModel(
            name='DeliveryAccident',
            fields=[
                ('WaybillNo', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('Recipient', models.CharField(max_length=100)),
                ('TotalFreight', models.IntegerField(default=0)),
                ('ProductValue', models.IntegerField(default=0)),
                ('Reimbursement', models.IntegerField(default=0)),
                ('ShippingDate', models.DateField()),
                ('PurchaseDate', models.ForeignKey(db_column='PurchaseDate', on_delete=django.db.models.deletion.CASCADE, to='MeatApp.purchase')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('empNo', models.CharField(max_length=10, unique=True, verbose_name='Employee Number')),
                ('username', models.CharField(max_length=30, unique=True, verbose_name='User name')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date joined')),
                ('Job', models.CharField(choices=[('OM', '주문담당자'), ('DM', '해체담당자'), ('WM', '입고담당자')], default='OM', max_length=50)),
                ('Position', models.CharField(choices=[('A', '관리자'), ('M', '매니저'), ('U', '사용자')], default='U', max_length=20)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('StockDate', models.DateField()),
                ('Stockitem', models.CharField(max_length=100)),
                ('RealWeight', models.IntegerField(default=0)),
                ('RealPrice', models.IntegerField(default=0)),
                ('MeterialNo', models.IntegerField(default=0)),
                ('SlaugtherDate', models.DateField()),
                ('UnitPrice', models.IntegerField(default=0)),
                ('StockNo', models.CharField(blank=True, max_length=100, unique=True)),
                ('StockSituation', models.CharField(max_length=100)),
                ('OrderNo', models.ForeignKey(db_column='OrderNo', on_delete=django.db.models.deletion.CASCADE, to='MeatApp.order', to_field='OrderNo', unique=True)),
                ('StockWorker', models.ForeignKey(db_column='StockWorker', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='empNo')),
            ],
        ),
        migrations.AddField(
            model_name='purchase',
            name='Purchaser',
            field=models.ForeignKey(db_column='Purchaser', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('ProductDate', models.DateTimeField(auto_now=True)),
                ('WeightAfterWork', models.IntegerField(default=0)),
                ('LossWeight', models.IntegerField(default=0)),
                ('ProductPrice', models.IntegerField(default=0)),
                ('DiscountRate', models.IntegerField(default=0)),
                ('ProductNo', models.CharField(blank=True, max_length=100, unique=True)),
                ('ProductSituation', models.CharField(max_length=100)),
                ('Quantity', models.IntegerField(default=0)),
                ('PurchaseNo', models.ForeignKey(blank=True, db_column='PurchaseNo', null=True, on_delete=django.db.models.deletion.SET_NULL, to='MeatApp.purchase', to_field='PurchaseNo')),
                ('StockNo', models.ForeignKey(db_column='StockNo', on_delete=django.db.models.deletion.CASCADE, to='MeatApp.stock', to_field='StockNo')),
                ('ProductWorker', models.ForeignKey(db_column='ProductWorker', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='empNo')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='OrderWorker',
            field=models.ForeignKey(db_column='OrderWorker', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='empNo'),
        ),
    ]
