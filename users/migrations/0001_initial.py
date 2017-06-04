# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.utils.timezone
from decimal import Decimal
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('currency', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(verbose_name='last login', blank=True, null=True)),
                ('is_superuser', models.BooleanField(verbose_name='superuser status', default=False, help_text='Designates that this user has all permissions without explicitly assigning them.')),
                ('username', models.CharField(verbose_name='Имя пользователя', max_length=40, unique=True)),
                ('email', models.EmailField(verbose_name='E-mail', max_length=254, unique=True)),
                ('date_joined', models.DateTimeField(verbose_name='Дата регистрации', default=django.utils.timezone.now)),
                ('is_active', models.BooleanField(verbose_name='Активный', default=True, help_text='Отметьте, если пользователь должен считаться активным. Уберите эту отметку вместо удаления аккаунта.')),
                ('is_staff', models.BooleanField(verbose_name='Статус персонала', default=False, help_text='Отметьте, если пользователь может входить в административную часть сайта.')),
                ('groups', models.ManyToManyField(verbose_name='groups', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group')),
                ('pair', models.ForeignKey(blank=True, null=True, editable=False, to='currency.TypePair')),
                ('user_permissions', models.ManyToManyField(verbose_name='user permissions', blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission')),
            ],
            options={
                'verbose_name': 'Профиль',
                'verbose_name_plural': 'Профили',
            },
        ),
        migrations.CreateModel(
            name='AddressBook',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('email', models.EmailField(verbose_name='E-Mail', max_length=254, unique=True)),
            ],
            options={
                'verbose_name': 'получателя',
                'verbose_name_plural': 'получатели',
            },
        ),
        migrations.CreateModel(
            name='ProfileBalance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created', models.DateTimeField(verbose_name='дата создания', auto_now_add=True)),
                ('updated', models.DateTimeField(verbose_name='дата изменения', auto_now=True)),
                ('value', models.DecimalField(verbose_name='количество', validators=[django.core.validators.MinValueValidator(Decimal('0'))], max_digits=14, decimal_places=8)),
                ('action', models.CharField(verbose_name='действие', max_length=1, choices=[('+', 'пополнение'), ('-', 'списание')], validators=[django.core.validators.RegexValidator(regex='^[+-]$', message='не допускаются значения кроме [+-]', code='invalid_action')])),
                ('bank', models.TextField(verbose_name='номер счета на ввод / вывод', max_length=255, blank=True, null=True)),
                ('user_bank', models.TextField(verbose_name='Реквизиты', max_length=255, blank=True, null=True)),
                ('accept', models.BooleanField(verbose_name='Подтвердить', default=False)),
                ('confirm', models.BooleanField(verbose_name='Подтверждено пользователем', default=True)),
                ('cancel', models.BooleanField(verbose_name='Отменить', default=False)),
                ('commission', models.DecimalField(verbose_name='Комиссия %', default=0.0, editable=False, validators=[django.core.validators.MinValueValidator(Decimal('0'))], max_digits=5, decimal_places=2)),
                ('min_commission', models.DecimalField(verbose_name='Минимальная комиссия', default=0.0, editable=False, validators=[django.core.validators.MinValueValidator(Decimal('0'))], max_digits=14, decimal_places=8)),
                ('max_commission', models.DecimalField(verbose_name='Максимальная комиссия', default=0.0, editable=False, validators=[django.core.validators.MinValueValidator(Decimal('0'))], max_digits=14, decimal_places=8)),
                ('paymethod', models.ForeignKey(to='currency.PaymentMethod')),
                ('profile', models.ForeignKey(verbose_name='Профиль', to=settings.AUTH_USER_MODEL)),
                ('valuta', models.ForeignKey(verbose_name='валюта', to='currency.Valuta')),
            ],
            options={
                'verbose_name': 'перевод',
                'verbose_name_plural': 'переводы средств',
            },
        ),
        migrations.CreateModel(
            name='ProfilePayNumber',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created', models.DateTimeField(verbose_name='дата создания', auto_now_add=True)),
                ('updated', models.DateTimeField(verbose_name='дата изменения', auto_now=True)),
                ('number', models.CharField(verbose_name='Номер счета', max_length=255)),
                ('paymethod', models.ForeignKey(blank=True, null=True, related_name='pay_number', to='currency.PaymentMethod')),
                ('profile', models.ForeignKey(verbose_name='Профиль', blank=True, null=True, help_text='Присваивается автоматически', related_name='pay_number', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProfileRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('role', models.CharField(verbose_name='Роль', max_length=15, choices=[('manager', 'Менеджер'), ('customer', 'клиент')])),
                ('profile', models.ForeignKey(verbose_name='Профиль', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Роль пользователя',
                'verbose_name_plural': 'Роли пользователя',
            },
        ),
        migrations.AlterUniqueTogether(
            name='profilerole',
            unique_together=set([('profile', 'role')]),
        ),
    ]
