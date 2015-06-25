# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0016_forecastanalysis_post_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membership',
            name='admin_rights',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='membership',
            name='track_forecasts',
            field=models.BooleanField(default=False),
        ),
    ]
