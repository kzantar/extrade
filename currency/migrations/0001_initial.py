# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from decimal import Decimal
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('disable', models.BooleanField(verbose_name='отключить', default=False)),
                ('enable_user_bank', models.BooleanField(verbose_name='Включить пользовательские реквизиты', default=False)),
                ('enable_account_number', models.BooleanField(verbose_name='уникальный номер счета из списка', default=False, help_text="<a href='../../../users/profilepaynumber/'>cписок</a>")),
                ('method', models.CharField(verbose_name='Метод оплаты', max_length=255)),
                ('action', models.CharField(verbose_name='действие', max_length=1, choices=[('+', 'пополнение'), ('-', 'списание')], validators=[django.core.validators.RegexValidator(regex='^[+-]$', message='не допускаются значения кроме [+-]', code='invalid_action')])),
                ('commission', models.DecimalField(verbose_name='Комиссия %', default=0.0, validators=[django.core.validators.MinValueValidator(Decimal('0'))], max_digits=5, decimal_places=2)),
                ('min_commission', models.DecimalField(verbose_name='Минимальная комиссия', default=0.0, validators=[django.core.validators.MinValueValidator(Decimal('0'))], max_digits=14, decimal_places=8)),
                ('max_commission', models.DecimalField(verbose_name='Максимальная комиссия', default=0.0, validators=[django.core.validators.MinValueValidator(Decimal('0'))], max_digits=14, decimal_places=8)),
                ('min_amount', models.DecimalField(verbose_name='Минимальная сумма', default=0.0, validators=[django.core.validators.MinValueValidator(Decimal('0'))], max_digits=14, decimal_places=8)),
                ('max_amount', models.DecimalField(verbose_name='Максимальная сумма', default=0.0, validators=[django.core.validators.MinValueValidator(Decimal('0'))], max_digits=14, decimal_places=8)),
                ('bank', models.TextField(verbose_name='номер счета', blank=True, null=True, help_text="При включенной опции 'уникальный номер счета из списка', номер подставляется в значение {{ pay_number }}<br>Виден после создания заявки.")),
                ('description_bank', models.TextField(verbose_name='описание', blank=True, null=True, help_text='видно до создания заявки')),
            ],
            options={
                'verbose_name': 'метод оплаты',
                'verbose_name_plural': 'методы оплаты',
            },
        ),
        migrations.CreateModel(
            name='TypePair',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('commission', models.DecimalField(default=0.0, max_digits=5, decimal_places=2)),
                ('slug', models.SlugField(editable=False)),
            ],
        ),
        migrations.CreateModel(
            name='Valuta',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('value', models.SlugField(unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='typepair',
            name='left',
            field=models.ForeignKey(related_name='left_right', to='currency.Valuta'),
        ),
        migrations.AddField(
            model_name='typepair',
            name='right',
            field=models.ForeignKey(related_name='funds_right', to='currency.Valuta'),
        ),
        migrations.AddField(
            model_name='paymentmethod',
            name='valuta',
            field=models.ForeignKey(related_name='payment_method', to='currency.Valuta'),
        ),
        migrations.AlterUniqueTogether(
            name='typepair',
            unique_together=set([('left', 'right')]),
        ),
    ]
