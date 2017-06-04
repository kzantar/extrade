# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import warrant.models
from decimal import Decimal
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('currency', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Orders',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('commission', models.DecimalField(verbose_name='Комиссия %', default=0.0, editable=False, validators=[django.core.validators.MinValueValidator(Decimal('0'))], max_digits=5, decimal_places=2)),
                ('amount', models.DecimalField(verbose_name='Количество', validators=[django.core.validators.MinValueValidator(Decimal('1E-7'))], max_digits=14, decimal_places=8)),
                ('rate', models.DecimalField(verbose_name='Стоимость', validators=[django.core.validators.MinValueValidator(Decimal('1E-7'))], max_digits=14, decimal_places=8)),
                ('cancel', models.BooleanField(verbose_name='отменен | отменен частично', default=False)),
                ('completed', models.BooleanField(verbose_name='Завершен', default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Buy',
            fields=[
                ('orders_ptr', models.OneToOneField(primary_key=True, serialize=False, auto_created=True, parent_link=True, to='warrant.Orders')),
            ],
            bases=('warrant.orders', warrant.models.Prop),
        ),
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('orders_ptr', models.OneToOneField(primary_key=True, serialize=False, auto_created=True, parent_link=True, to='warrant.Orders')),
                ('buy', models.ForeignKey(verbose_name='Покупка', blank=True, null=True, related_name='buy_buy', to='warrant.Buy')),
            ],
            bases=('warrant.orders', warrant.models.Prop),
        ),
        migrations.AddField(
            model_name='orders',
            name='pair',
            field=models.ForeignKey(related_name='warrant_orders_related', to='currency.TypePair'),
        ),
        migrations.AddField(
            model_name='orders',
            name='user',
            field=models.ForeignKey(related_name='warrant_orders_related', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='buy',
            name='sale',
            field=models.ForeignKey(verbose_name='Продажа', blank=True, null=True, related_name='sale_sale', to='warrant.Sale'),
        ),
    ]
