# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0003_auto_20150707_0946'),
    ]

    operations = [
        migrations.RenameField(
            model_name='forecastvotechoiceinline',
            old_name='forecast',
            new_name='forecast_question',
        ),
    ]
