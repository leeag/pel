# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0011_auto_20150618_0816'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuserprofile',
            name='user',
            field=models.OneToOneField(related_name='custom', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='forecast',
            name='max',
            field=models.IntegerField(default=100, blank=True),
        ),
        migrations.AlterField(
            model_name='forecast',
            name='min',
            field=models.IntegerField(default=0, blank=True),
        ),
    ]
