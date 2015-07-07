# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0006_auto_20150707_1019'),
    ]

    operations = [
        migrations.AddField(
            model_name='forecast',
            name='choice',
            field=models.CharField(max_length=150, blank=True),
        ),
    ]
