from datetime import date
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from django.db import models
from django.db.models import Count, Avg
from taggit.managers import TaggableManager

import forecast.settings as settings
from forecast.settings import ORGANIZATION_TYPE, FORECAST_TYPE, STATUS_CHOICES, GROUP_TYPES, REGIONS


def _votes_by_forecast_type(forecast):
    if forecast.forecast_type == settings.FORECAST_TYPE_FINITE:
        votes = [{'choice': v['choice__choice'], 'votesCount': v['votes_count']}
                 for v in forecast.votes.all().values('choice__choice').annotate(votes_count=Count('choice__choice'))]
    elif forecast.forecast_type == settings.FORECAST_TYPE_MAGNITUDE:
        votes = [{'date': v['date'].strftime('%Y-%m-%d'), 'avgVotes': (v['avg_votes'] + v['avg_votes2']) / 2}
                 for v in forecast.votes.values('date').annotate(avg_votes=Avg('vote'), avg_votes2=Avg('vote2'))]
    else:
        votes = [{'date': v['date'].strftime('%Y-%m-%d'), 'avgVotes': v['avg_votes']}
                 for v in forecast.votes.values('date').annotate(avg_votes=Avg('vote'))]
    return votes


class ForecastsManager(models.Manager):
    TYPE_ACTIVE = 1
    TYPE_ARCHIVED = 2

    def __init__(self, *args, **kwargs):
        self.forecasts_type = kwargs.pop('forecasts_type', self.TYPE_ACTIVE)
        super(ForecastsManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        qs = super(ForecastsManager, self).get_queryset()
        if self.forecasts_type == self.TYPE_ACTIVE:
            return qs.filter(end_date__gte=date.today())
        else:
            return qs.filter(end_date__lt=date.today())


class CustomUserProfile(models.Model):
    user = models.OneToOneField(User)
    display_only_username = models.BooleanField(default=False)
    country = CountryField(blank=False)
    city = models.CharField(max_length=50, blank=True)
    profession = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=100, blank=True)
    organization = models.CharField(choices=ORGANIZATION_TYPE, max_length=2)
    organization_name = models.TextField(blank=True)
    forecast_areas = models.CommaSeparatedIntegerField(max_length=3, blank=True)
    forecast_regions = models.CommaSeparatedIntegerField(max_length=3, blank=True)

    activation_token = models.TextField(blank=True, max_length=256)
    expires_at = models.DateTimeField(blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    conditions_accepted = models.BooleanField(default=False)


class Forecast(models.Model):
    forecast_type = models.CharField(max_length=2, choices=FORECAST_TYPE)
    forecast_question = models.TextField(max_length=1000)
    min = models.IntegerField(blank=True, default=0)
    max = models.IntegerField(blank=True, default=100)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField()
    tags = TaggableManager()

    objects = models.Manager()
    active = ForecastsManager(forecasts_type=ForecastsManager.TYPE_ACTIVE)
    archived = ForecastsManager(forecasts_type=ForecastsManager.TYPE_ARCHIVED)

    class Meta:
        db_table = 'forecasts'
        get_latest_by = 'start_date'
        ordering = ['-end_date']

    def is_active(self):
        return self.end_date >= date.today()

    def __unicode__(self):
        return '%s' % self.forecast_question

    def votes_count(self):
        votes = Forecast.objects.filter(pk=self.id).annotate(votes_count=Count('votes')).get().votes_count
        return votes
    votes_count.admin_order_field = 'votes_count'

    def to_json(self):
        response = {
            'id': self.id,
            'forecastType': self.get_forecast_type_display(),
            'forecastQuestion': self.forecast_question,
            'startDate': self.start_date.strftime('%Y-%m-%d'),
            'endDate': self.end_date.strftime('%Y-%m-%d'),
            'votes': _votes_by_forecast_type(self)}
        try:
            response['forecastersCount'] = self.votes.values('forecast') \
                .annotate(forecasters=Count('user', distinct=True)).get()['forecasters']
        except ForecastVotes.DoesNotExist:
            response['forecastersCount'] = 0
        return response


class ForecastPropose(models.Model):
    user = models.ForeignKey(User)
    forecast_type = models.CharField(max_length=2, choices=FORECAST_TYPE)
    forecast_question = models.TextField(max_length=1000)
    end_date = models.DateField(default=date.today)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='u')
    tags = TaggableManager()

    def __unicode__(self):
        return self.forecast_question


class ForecastVotes(models.Model):
    user = models.ForeignKey(User)
    forecast = models.ForeignKey('Forecast', related_name='votes')
    vote = models.IntegerField(blank=True, null=True)
    vote2 = models.IntegerField(blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    choice = models.ForeignKey('ForecastVoteChoice', blank=True, null=True)

    class Meta:
        verbose_name = 'forecast vote'
        verbose_name_plural = 'forecast votes'

    def get_vote(self):
        if self.forecast.forecast_type == settings.FORECAST_TYPE_FINITE:
            return self.choice.choice
        elif self.forecast.forecast_type == settings.FORECAST_TYPE_MAGNITUDE:
            return u"%s \u2014 %s" % (self.vote, self.vote2)
        return self.vote


class ForecastAnalysis(models.Model):
    user = models.ForeignKey(User)
    forecast = models.ForeignKey('Forecast')
    title = models.CharField(max_length=100, blank=True, null=True)
    body = models.TextField(max_length=1000, blank=True, null=True)

    def __unicode__(self):
        return self.title


class ForecastAnalysisVote(models.Model):
    user = models.ForeignKey(User)
    analysis = models.ForeignKey('ForecastAnalysis', related_name='analysis_votes')
    vote = models.IntegerField(choices=settings.ANALYSIS_VOTE_CHOICES)


class ForecastMedia(models.Model):
    forecast = models.ForeignKey('Forecast')
    name = models.CharField(max_length=100, blank=True, null=True)
    url = models.URLField()
    image = models.ImageField()

    def __unicode__(self):
        return self.name if self.name else self.url


class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=300, blank=True, null=True)
    type = models.CharField(max_length=1, choices=GROUP_TYPES)
    organization_type = models.CharField(max_length=1, choices=ORGANIZATION_TYPE, blank=True, null=True)
    region = models.CharField(max_length=1, choices=REGIONS, blank=True, null=True)

    def __unicode__(self):
        return self.name


class Membership(models.Model):
    user = models.ForeignKey(User)
    group = models.ForeignKey('Group')
    date_joined = models.DateTimeField(auto_now_add=True)
    admin_rights = models.BooleanField()
    track_forecasts = models.BooleanField()

    def __unicode__(self):
        return self.user.username + ' in ' + self.group.name


class ForecastVoteChoice(models.Model):
    forecast = models.ForeignKey('Forecast', related_name='choices')
    num = models.IntegerField(unique=True)
    choice = models.CharField(max_length=150)

    def __unicode__(self):
        return self.choice
