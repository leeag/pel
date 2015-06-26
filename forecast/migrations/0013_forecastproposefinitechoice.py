# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0012_auto_20150618_1628'),
    ]

    operations = [
        migrations.CreateModel(
            name='ForecastProposeFiniteChoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('choice_fin', models.CharField(max_length=150)),
                ('forecast', models.ForeignKey(to='forecast.Forecast')),
            ],
        ),
    ]
