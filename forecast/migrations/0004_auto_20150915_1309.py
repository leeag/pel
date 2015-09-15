# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0003_auto_20150914_1202'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='name_en',
            field=models.CharField(max_length=50, null=True, verbose_name=b'name'),
        ),
        migrations.AddField(
            model_name='city',
            name='name_ru',
            field=models.CharField(max_length=50, null=True, verbose_name=b'name'),
        ),
        migrations.AddField(
            model_name='city',
            name='name_uk',
            field=models.CharField(max_length=50, null=True, verbose_name=b'name'),
        ),
        migrations.AddField(
            model_name='country',
            name='name_en',
            field=models.CharField(max_length=50, null=True, verbose_name=b'name'),
        ),
        migrations.AddField(
            model_name='country',
            name='name_ru',
            field=models.CharField(max_length=50, null=True, verbose_name=b'name'),
        ),
        migrations.AddField(
            model_name='country',
            name='name_uk',
            field=models.CharField(max_length=50, null=True, verbose_name=b'name'),
        ),
        migrations.AddField(
            model_name='country',
            name='region_name_en',
            field=models.CharField(max_length=50, null=True, verbose_name=b'region name', blank=True),
        ),
        migrations.AddField(
            model_name='country',
            name='region_name_ru',
            field=models.CharField(max_length=50, null=True, verbose_name=b'region name', blank=True),
        ),
        migrations.AddField(
            model_name='country',
            name='region_name_uk',
            field=models.CharField(max_length=50, null=True, verbose_name=b'region name', blank=True),
        ),
        migrations.AddField(
            model_name='region',
            name='name_en',
            field=models.CharField(max_length=50, null=True, verbose_name=b'name'),
        ),
        migrations.AddField(
            model_name='region',
            name='name_ru',
            field=models.CharField(max_length=50, null=True, verbose_name=b'name'),
        ),
        migrations.AddField(
            model_name='region',
            name='name_uk',
            field=models.CharField(max_length=50, null=True, verbose_name=b'name'),
        ),
    ]
