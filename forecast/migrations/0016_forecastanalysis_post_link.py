# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0015_remove_forecastvotes_vote2'),
    ]

    operations = [
        migrations.AddField(
            model_name='forecastanalysis',
            name='post_link',
            field=models.URLField(null=True, blank=True),
        ),
    ]
