# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forecast', '0003_auto_20150723_1011'),
    ]

    operations = [
        migrations.CreateModel(
            name='Visitors',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('visited', models.ForeignKey(related_name='visited', to=settings.AUTH_USER_MODEL)),
                ('visitor', models.ForeignKey(related_name='visitor', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Visitors',
            },
        ),
    ]
