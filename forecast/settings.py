ORGANIZATION_TYPE = (('1', 'School'),
                     ('2', 'Think Tank'),
                     ('3', 'Company'),
                     ('4', 'Government Agency'))

FORECAST_TYPE_FINITE = '1'
FORECAST_TYPE_PROBABILITY = '2'
FORECAST_TYPE_MAGNITUDE = '3'
FORECAST_TYPE_TIME_HORIZON = '4'

FORECAST_TYPE = ((FORECAST_TYPE_FINITE, 'Finite Event'),
                 (FORECAST_TYPE_PROBABILITY, 'Probability'),
                 (FORECAST_TYPE_MAGNITUDE, 'Magnitude'),
                 (FORECAST_TYPE_TIME_HORIZON, 'Time Horizon Event'))

AREAS = (('1', "International Security Treaties"),
         ('2', "Wars/Conflicts/Border Issues"),
         ('3', "Revolutions/Coups"),
         ('4', "Nuclear Weapons Issues"),
         ('5', "Terrorism"),
         ('6', "Energy"),
         ('7', "Labor/Industrial Action Issues"),
         ('8', "International Trade Alliances and Deals"),
         ('9', "Central Bank Decisions"),
         ('10', "Sovereign Debt Issues"))

REGIONS = (('1', "Global"),
           ('2', "Western Europe"),
           ('3', "Eastern Europe"),
           ('4', "North America"),
           ('5', "Central America"),
           ('6', "South America"),
           ('7', "Middle East"),
           ('8', "North Africa"),
           ('9', "Central Africa"),
           ('10', "Sub-Saharan Africa"),
           ('11', "Russia"),
           ('12', "Near-East Asia"),
           ('13', "East Asia"),
           ('14', "South East Asia"),
           ('15', "South Pacific"))

STATUS_CHOICES = (('u', "Unpublished"),
                  ('p', "Published"))

ANALYSIS_VOTE_CHOICES = ((1, "Not Useful"),
                         (2, "Somewhat Useful"),
                         (3, "Useful"),
                         (4, "Very Useful"),
                         (5, "Highly Useful"))

FORECAST_FILTER = "filter"
FORECAST_FILTER_MOST_ACTIVE = "mostactive"
FORECAST_FILTER_NEWEST = "newest"
FORECAST_FILTER_CLOSING = "closing"
FORECAST_FILTER_ARCHIVED = "archived"

FORECAST_FILTERS = {'FORECAST_FILTER_MOST_ACTIVE': FORECAST_FILTER_MOST_ACTIVE,
                    'FORECAST_FILTER_NEWEST': FORECAST_FILTER_NEWEST,
                    'FORECAST_FILTER_CLOSING': FORECAST_FILTER_CLOSING}

GROUP_TYPES = (('1', 'Public'),
               ('2', 'Private'))

