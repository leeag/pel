# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0013_group_admin_approved'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='forecastvotechoice',
            name='num',
        ),
    ]
