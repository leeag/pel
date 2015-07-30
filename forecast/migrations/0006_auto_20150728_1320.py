# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0001_initial'),
        ('forecast', '0005_auto_20150728_1250'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='forecast',
            name='forecast_areas',
        ),
        migrations.RemoveField(
            model_name='forecast',
            name='forecast_regions',
        ),
        migrations.AddField(
            model_name='forecast',
            name='tags',
            field=taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', help_text='A comma-separated list of tags.', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='forecastpropose',
            name='tags',
            field=taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', help_text='A comma-separated list of tags.', verbose_name='Tags'),
        ),
    ]
