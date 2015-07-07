# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0002_auto_20150706_1257'),
    ]

    operations = [
        migrations.RenameField(
            model_name='forecastvotechoiceinline',
            old_name='choice',
            new_name='choiceline',
        ),
    ]
