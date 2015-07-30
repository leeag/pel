# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0006_auto_20150728_1320'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='forecast',
            name='tags',
        ),
        migrations.AddField(
            model_name='forecast',
            name='forecast_areas',
            field=models.CommaSeparatedIntegerField(max_length=100, blank=True),
        ),
        migrations.AddField(
            model_name='forecast',
            name='forecast_regions',
            field=models.CommaSeparatedIntegerField(max_length=100, blank=True),
        ),
    ]
