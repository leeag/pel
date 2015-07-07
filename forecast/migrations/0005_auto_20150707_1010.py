# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0004_auto_20150707_1003'),
    ]

    operations = [
        migrations.CreateModel(
            name='ForecastVoteChoiceFinite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('choiceline', models.CharField(max_length=150)),
                ('forecast_question', models.ForeignKey(to='forecast.ForecastPropose')),
            ],
        ),
        migrations.RemoveField(
            model_name='forecastvotechoiceinline',
            name='forecast_question',
        ),
        migrations.DeleteModel(
            name='ForecastVoteChoiceInline',
        ),
    ]
