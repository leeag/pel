# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0013_forecastproposefinitechoice'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='forecastproposefinitechoice',
            name='forecast',
        ),
        migrations.AddField(
            model_name='forecastpropose',
            name='choice',
            field=models.CharField(max_length=150, blank=True),
        ),
        migrations.DeleteModel(
            name='ForecastProposeFiniteChoice',
        ),
    ]
