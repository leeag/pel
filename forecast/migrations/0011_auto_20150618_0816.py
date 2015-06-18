# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0010_forecastanalysisvote'),
    ]

    operations = [
        migrations.AddField(
            model_name='forecast',
            name='max',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='forecast',
            name='min',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='forecastanalysisvote',
            name='analysis',
            field=models.ForeignKey(related_name='analysis_votes', to='forecast.ForecastAnalysis'),
        ),
    ]
