# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0002_auto_20150706_1257'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='region',
            field=models.CharField(blank=True, max_length=1, null=True, choices=[(b'1', b'Global'), (b'2', b'Western Europe'), (b'3', b'Eastern Europe'), (b'4', b'North America'), (b'5', b'Central America'), (b'6', b'South America'), (b'7', b'Middle East'), (b'8', b'North Africa'), (b'9', b'Central Africa'), (b'10', b'Sub-Saharan Africa'), (b'11', b'Russia'), (b'12', b'Near-East Asia'), (b'13', b'East Asia'), (b'14', b'South East Asia'), (b'15', b'South Pacific')]),
        ),
    ]
