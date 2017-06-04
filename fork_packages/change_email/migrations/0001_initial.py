# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailChange',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('new_email', models.EmailField(verbose_name='new email address', max_length=254, help_text='The new email address that still needs to be confirmed.')),
                ('date', models.DateTimeField(verbose_name='date', help_text='The date and time the email address change was requested.', auto_now_add=True)),
                ('site', models.ForeignKey(blank=True, null=True, to='sites.Site')),
                ('user', models.OneToOneField(verbose_name='user', help_text='The user that has requested the email address change.', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'email address change request',
                'verbose_name_plural': 'email address change requests',
                'get_latest_by': 'date',
            },
        ),
    ]
