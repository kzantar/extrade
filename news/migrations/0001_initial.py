# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('date', models.DateTimeField(verbose_name='Дата')),
                ('title', models.CharField(verbose_name='Заголовок', max_length=255)),
                ('smalltext', models.TextField(verbose_name='Вводный абзац')),
                ('text', models.TextField(verbose_name='Текст')),
            ],
            options={
                'verbose_name': 'новость',
                'verbose_name_plural': 'Новости',
            },
        ),
    ]
