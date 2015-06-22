from datetime import date

from django.contrib import admin
from django.contrib.admin import ModelAdmin, StackedInline, TabularInline
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count
from django import forms

from django_object_actions import DjangoObjectActions

import models
from forecast import settings

admin.site.site_header = 'Peleus administration'
admin.site.site_title = 'Peleus site admin'


class CustomUserProfileInline(StackedInline):
    model = models.CustomUserProfile
    verbose_name = 'forecast user'
    verbose_name_plural = 'forecast users'

UserAdmin.inlines = (CustomUserProfileInline,)


class IsActiveDisplayFilter(admin.SimpleListFilter):
    title = 'status'
    parameter_name = 'is_active_status'
    ACTIVE = 'active'
    ARCHIVED = 'archived'

    def lookups(self, request, model_admin):
        return (
            (self.ACTIVE, 'Active'),
            (self.ARCHIVED, 'Archived'),
        )

    def queryset(self, request, qs):
        v = self.value()
        qs = qs.annotate(votes_count=Count('votes'))

        if v == self.ACTIVE:
            return qs.filter(end_date__gte=date.today())
        elif v == self.ARCHIVED:
            return qs.filter(end_date__lt=date.today())
        else:
            return qs


class ForecastMediaInline(TabularInline):
    model = models.ForecastMedia
    verbose_name = "media"
    extra = 1


class ForecastAnalysisInline(StackedInline):
    model = models.ForecastAnalysis
    verbose_name = "post"
    extra = 1


class ForecastVoteChoicesInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        # get forms that actually have valid data
        forecast_type = self.forms[0].data.get('forecast_type')
        if forecast_type == settings.FORECAST_TYPE_FINITE:
            count = 0
            for form in self.forms:
                try:
                    if form.cleaned_data:
                        count += 1
                except AttributeError:
                    # annoyingly, if a subform is invalid Django explicity raises
                    # an AttributeError for cleaned_data
                    pass
            if count < 2:
                raise forms.ValidationError('You must have at least two orders')


class ForecastVoteChoicesInline(TabularInline):
    formset = ForecastVoteChoicesInlineFormset
    verbose_name = 'vote choice'
    verbose_name_plural = 'vote choices (for finite events only)'
    extra = 2
    model = models.ForecastVoteChoice


class PublishedProposeFilter(admin.SimpleListFilter):
    title = 'status'
    parameter_name = 'publication_status'
    YES = 'no'
    ALL = 'all'

    def lookups(self, request, model_admin):
        return (
            (None, 'Unpublished'),
            (self.YES, 'Published'),
            (self.ALL, 'All')
        )

    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup,
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }

    def queryset(self, request, queryset):
        v = self.value()

        if v is None:
            return queryset.filter(status='u')
        elif v == self.YES:
            return queryset.filter(status='p')
        else:
            return queryset


@admin.register(models.Forecast)
class ForecastAdmin(ModelAdmin):
    list_display = ('forecast_question', 'forecast_type', 'start_date', 'end_date', 'votes_count')
    change_form_template = 'admin/_change_form.html'
    list_filter = ('forecast_type', IsActiveDisplayFilter,)
    inlines = (ForecastVoteChoicesInline, ForecastMediaInline, ForecastAnalysisInline,)

    def save_model(self, request, obj, form, change):
        obj.save()

    # def render_change_form(self, request, context, *args, **kwargs):
    #     """
    #     Refrain from prolonged exposure.
    #     https://gist.github.com/yuchant/839996
    #     """
    #     def get_queryset(original_func):
    #         import inspect, itertools
    #         def wrapped_func():
    #             if inspect.stack()[1][3] == '__iter__':
    #                 return itertools.repeat(None)
    #             return original_func()
    #         return wrapped_func
    #
    #     for formset in context['inline_admin_formsets']:
    #         formset.formset.get_queryset = get_queryset(formset.formset.get_queryset)
    #
    #     return super(ForecastAdmin, self).render_change_form(request, context, *args, **kwargs)


@admin.register(models.ForecastAnalysis)
class ForecastAnalysisAdmin(ModelAdmin):
    list_display = ('user', 'title')


@admin.register(models.ForecastPropose)
class ForecastProposeAdmin(DjangoObjectActions, ModelAdmin):
    list_display = ('forecast_question', 'forecast_type', 'end_date', 'status')
    list_filter = (PublishedProposeFilter,)

    objectactions = ['publish_propose']

    exclude = ('status',)

    def has_add_permission(self, request):
        return False

    def publish_propose(self, request, obj):
        obj.status = 'p'
        obj.save()

        f = models.Forecast(forecast_type=obj.forecast_type,
                            forecast_question=obj.forecast_question,
                            end_date=obj.end_date)
        f.save()

        for tag in obj.tags.all():
            f.tags.add(tag)
    publish_propose.label = 'Publish'
    publish_propose.attrs = {'class': 'btn btn-primary'}

    def get_object_actions(self, request, context, **kwargs):
        if 'original' in context and context['original'] and context['original'].status != 'p':
            return ['publish_propose']
        return []


@admin.register(models.ForecastVotes)
class ForecastVotesAdmin(ModelAdmin):
    list_display = ('user_display', 'forecast_question_display', 'vote', 'date',)

    def user_display(self, obj):
        return obj.user
    user_display.short_description = 'User'
    user_display.admin_order_field = 'user'

    def forecast_question_display(self, obj):
        return obj.forecast.forecast_question
    forecast_question_display.short_description = 'Question'


@admin.register(models.Group)
class GroupAdmin(ModelAdmin):
    list_display = ('name', 'type')


@admin.register(models.Membership)
class MembershipAdmin(ModelAdmin):
    list_display = ('user', 'group')


@admin.register(models.ForecastAnalysisVote)
class AnalysisVoteAdmin(ModelAdmin):
    list_display = ('vote', 'user', 'analysis')
    list_filter = ('vote',)