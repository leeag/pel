# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0012_auto_20150618_1628'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='admin_approved',
            field=models.BooleanField(default=True),
        ),
    ]
