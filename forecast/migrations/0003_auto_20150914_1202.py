# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forecast', '0002_auto_20150812_1318'),
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name=b'name')),
            ],
            options={
                'verbose_name': 'Country/Region/City',
                'verbose_name_plural': 'Country/Region/Cities',
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name=b'name')),
                ('region_name', models.CharField(max_length=50, null=True, verbose_name=b'region name', blank=True)),
            ],
            options={
                'verbose_name': 'country',
                'verbose_name_plural': 'countries',
            },
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name=b'name')),
                ('country', models.ForeignKey(related_name='regions', verbose_name=b'country', to='forecast.Country')),
            ],
            options={
                'verbose_name': 'Country/Region',
                'verbose_name_plural': 'Country/Regions',
            },
        ),
        migrations.AddField(
            model_name='city',
            name='country',
            field=models.ForeignKey(related_name='cities', verbose_name=b'country', to='forecast.Country'),
        ),
        migrations.AddField(
            model_name='city',
            name='region',
            field=models.ForeignKey(related_name='cities', verbose_name=b'region', blank=True, to='forecast.Region', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='region',
            unique_together=set([('name', 'country')]),
        ),
    ]
