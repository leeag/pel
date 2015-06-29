# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0018_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='ForecastProposeFiniteChoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('choice', models.CharField(max_length=150)),
            ],
        ),
        migrations.RemoveField(
            model_name='forecastpropose',
            name='choice',
        ),
        migrations.AddField(
            model_name='forecastproposefinitechoice',
            name='forecast',
            field=models.ForeignKey(to='forecast.ForecastPropose'),
        ),
    ]
