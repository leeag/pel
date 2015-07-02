# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django_countries.fields
from django.conf import settings
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('display_only_username', models.BooleanField(default=False)),
                ('country', django_countries.fields.CountryField(max_length=2)),
                ('city', models.CharField(max_length=50, blank=True)),
                ('profession', models.CharField(max_length=100, blank=True)),
                ('position', models.CharField(max_length=100, blank=True)),
                ('organization', models.CharField(max_length=2, choices=[(b'1', b'School'), (b'2', b'Think Tank'), (b'3', b'Company'), (b'4', b'Government Agency')])),
                ('organization_name', models.TextField(blank=True)),
                ('forecast_areas', models.CommaSeparatedIntegerField(max_length=100, blank=True)),
                ('forecast_regions', models.CommaSeparatedIntegerField(max_length=100, blank=True)),
                ('activation_token', models.TextField(max_length=256, blank=True)),
                ('expires_at', models.DateTimeField(null=True, blank=True)),
                ('email_verified', models.BooleanField(default=False)),
                ('conditions_accepted', models.BooleanField(default=False)),
                ('user', models.OneToOneField(related_name='custom', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Forecast',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('forecast_type', models.CharField(max_length=2, choices=[(b'1', b'Finite Event'), (b'2', b'Probability'), (b'3', b'Magnitude'), (b'4', b'Time Horizon Event')])),
                ('forecast_question', models.TextField(max_length=1000)),
                ('min', models.IntegerField(default=0, blank=True)),
                ('max', models.IntegerField(default=100, blank=True)),
                ('start_date', models.DateField(auto_now_add=True)),
                ('end_date', models.DateField()),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', help_text='A comma-separated list of tags.', verbose_name='Tags')),
            ],
            options={
                'ordering': ['-end_date'],
                'db_table': 'forecasts',
                'get_latest_by': 'start_date',
            },
        ),
        migrations.CreateModel(
            name='ForecastAnalysis',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('post_link', models.URLField(null=True, blank=True)),
                ('title', models.CharField(max_length=100, null=True, blank=True)),
                ('body', models.TextField(max_length=1000, null=True, blank=True)),
                ('forecast', models.ForeignKey(to='forecast.Forecast')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ForecastAnalysisVote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('vote', models.IntegerField(choices=[(1, b'Not Useful'), (2, b'Somewhat Useful'), (3, b'Useful'), (4, b'Very Useful'), (5, b'Highly Useful')])),
                ('analysis', models.ForeignKey(related_name='analysis_votes', to='forecast.ForecastAnalysis')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ForecastMedia',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, null=True, blank=True)),
                ('url', models.URLField()),
                ('image', models.ImageField(upload_to=b'')),
                ('forecast', models.ForeignKey(to='forecast.Forecast')),
            ],
        ),
        migrations.CreateModel(
            name='ForecastPropose',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('forecast_type', models.CharField(max_length=2, choices=[(b'1', b'Finite Event'), (b'2', b'Probability'), (b'3', b'Magnitude'), (b'4', b'Time Horizon Event')])),
                ('forecast_question', models.TextField(max_length=1000)),
                ('end_date', models.DateField(default=datetime.date.today)),
                ('status', models.CharField(default=b'u', max_length=1, choices=[(b'u', b'Unpublished'), (b'p', b'Published')])),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', help_text='A comma-separated list of tags.', verbose_name='Tags')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ForecastProposeFiniteChoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('choice', models.CharField(max_length=150)),
                ('forecast', models.ForeignKey(to='forecast.ForecastPropose')),
            ],
        ),
        migrations.CreateModel(
            name='ForecastVoteChoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('choice', models.CharField(max_length=150)),
                ('forecast', models.ForeignKey(related_name='choices', to='forecast.Forecast')),
            ],
        ),
        migrations.CreateModel(
            name='ForecastVotes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('vote', models.IntegerField(null=True, blank=True)),
                ('date', models.DateField(auto_now_add=True)),
                ('choice', models.ForeignKey(blank=True, to='forecast.ForecastVoteChoice', null=True)),
                ('forecast', models.ForeignKey(related_name='votes', to='forecast.Forecast')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'forecast vote',
                'verbose_name_plural': 'forecast votes',
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(max_length=300, null=True, blank=True)),
                ('type', models.CharField(max_length=1, choices=[(b'1', b'Public'), (b'2', b'Private')])),
                ('organization_type', models.CharField(blank=True, max_length=1, null=True, choices=[(b'1', b'School'), (b'2', b'Think Tank'), (b'3', b'Company'), (b'4', b'Government Agency')])),
                ('region', models.CharField(blank=True, max_length=1, null=True, choices=[(b'1', b'Europe'), (b'2', b'Middle East'), (b'3', b'Africa'), (b'4', b'Asia'), (b'5', b'South Pacific'), (b'6', b'North America'), (b'7', b'South America')])),
                ('admin_approved', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
                ('admin_rights', models.BooleanField(default=False)),
                ('track_forecasts', models.BooleanField(default=False)),
                ('group', models.ForeignKey(to='forecast.Group')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
