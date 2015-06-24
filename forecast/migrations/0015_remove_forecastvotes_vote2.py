# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0014_remove_forecastvotechoice_num'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='forecastvotes',
            name='vote2',
        ),
    ]
