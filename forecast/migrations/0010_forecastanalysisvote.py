# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forecast', '0009_auto_20150614_2139'),
    ]

    operations = [
        migrations.CreateModel(
            name='ForecastAnalysisVote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('vote', models.IntegerField(choices=[(1, b'Not Useful'), (2, b'Somewhat Useful'), (3, b'Useful'), (4, b'Very Useful'), (5, b'Highly Useful')])),
                ('analysis', models.ForeignKey(to='forecast.ForecastAnalysis')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
