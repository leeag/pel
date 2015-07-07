# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0005_auto_20150707_1010'),
    ]

    operations = [
        migrations.RenameField(
            model_name='forecastvotechoicefinite',
            old_name='choiceline',
            new_name='choice',
        ),
    ]
