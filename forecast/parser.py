# -*- coding: utf-8 -*-
import os
import sys
import django

sys.path.append(r'/home/aspire/PycharmProjects/Peleus/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'Peleus.settings'
django.setup()

from forecast.models import Country, Region, City
from django.utils import translation

translation.activate('en')
with open('countries_regions_cities.csv') as f:
    content = f.readlines()


for row in content:
    cells = row.split(',')
    country = Country()
    region = Region()
    if cells[0] != '':
        country = Country()
        country.name = cells[0]
        country.save()
    elif cells[1] != '':
        region = Region()
        region.name = cells[1]
        region.country = country
        region.save()
    # elif cells[4] != '':
    #     city = City()
    #     city.name = cells[4]
    #     city.region = region
    #     city.country = country
    # elif cells[6] != '':
    #     city = City()
    #     city.name = cells[6]
    #     city.region = region
    #     city.country = country