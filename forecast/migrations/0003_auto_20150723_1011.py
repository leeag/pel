# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0002_followers'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='followers',
            name='second_user',
        ),
        migrations.RemoveField(
            model_name='followers',
            name='user',
        ),
        migrations.DeleteModel(
            name='Followers',
        ),
    ]
