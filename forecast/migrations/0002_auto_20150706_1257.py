# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ForecastVoteChoiceInline',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('choice', models.CharField(max_length=150)),
                ('forecast', models.ForeignKey(to='forecast.ForecastPropose')),
            ],
        ),
        migrations.RemoveField(
            model_name='forecastproposefinitechoice',
            name='forecast',
        ),
        migrations.DeleteModel(
            name='ForecastProposeFiniteChoice',
        ),
    ]
