from models import CustomUserProfile
from forecast.settings import REGIONS, AREAS, FORECAST_FILTER, FORECAST_FILTERS

FORECAST_REGIONS = dict(REGIONS)
FORECAST_AREAS = dict(AREAS)


def forecast_user(request):
    try:
        custom_user = CustomUserProfile.objects.select_related().get(user_id=request.user.id)

        custom_user.forecast_areas = custom_user.forecast_areas.split(',')
        custom_user.forecast_regions = custom_user.forecast_regions.split(',')
    except (CustomUserProfile.DoesNotExist, ValueError, SyntaxError):
        custom_user = None

    return {'forecast_user': custom_user}


def forecast_stuff(_):
    interests = {'FORECAST_REGIONS': FORECAST_REGIONS, 'FORECAST_AREAS': FORECAST_AREAS}
    filters = dict(FORECAST_FILTERS.items() + [('FORECAST_FILTER', FORECAST_FILTER)])
    charts = dict((('FORECAST_TYPE_FINITE', '1'),
                   ('FORECAST_TYPE_PROBABILITY', '2'),
                   ('FORECAST_TYPE_MAGNITUDE', '3'),
                   ('FORECAST_TYPE_TIME_HORIZON', '4')))

    stuff = dict()
    stuff.update(interests)
    stuff.update(filters)
    stuff.update(charts)

    return stuff


# def forecast_filters(_):
#     return dict(FORECAST_FILTERS.items() + [('FORECAST_FILTER', FORECAST_FILTER)])
