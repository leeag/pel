from datetime import date

from django.contrib import admin
from django.contrib.admin import ModelAdmin, StackedInline
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count

import models


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


@admin.register(models.Forecast)
class ForecastAdmin(ModelAdmin):
    list_display = ('forecast_question', 'forecast_type', 'start_date', 'end_date', 'votes_count')
    list_filter = ('forecast_type', IsActiveDisplayFilter,)


@admin.register(models.ForecastPropose)
class ForecastAdmin(ModelAdmin):
    list_display = ('forecast_question_new', 'forecast_type_new', 'date', 'status')
    actions = ['make_published']

    def make_published(self, request, queryset):
        rows_updated = queryset.update(status='p')
        if rows_updated == 1:
            message_bit = "1 forecast was"
        else:
            message_bit = "%s forecasts were" % rows_updated
        self.message_user(request, "%s successfully marked as published." % message_bit)


@admin.register(models.ForecastVotes)
class ForecastVotesAdmin(ModelAdmin):
    list_display = ('user_display', 'forecast_question_display', 'vote', 'date',)

    def user_display(self, obj):
        return obj.user_id
    user_display.short_description = 'User'
    user_display.admin_order_field = 'user_id'

    def forecast_question_display(self, obj):
        return obj.forecast_id.forecast_question
    forecast_question_display.short_description = 'Question'

