# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forecast', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Followers',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_join', models.DateField(auto_now=True)),
                ('second_user', models.ForeignKey(related_name='second_user', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(related_name='first_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
