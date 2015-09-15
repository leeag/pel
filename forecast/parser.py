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


ci = City()

for row in content:
    cells = row.split(',')
    if cells[0] != '':
        co = Country()
        co.name = cells[0]    #Country name adding (Україна, Polska..)
        print co.name
        co.save()
    elif cells[1] != '':
        re = Region()
        country = Country.objects.get(name=cells[0])
        re.name = cells[1]    #Region name adding (Львівська, Małopolskie ..)
        re.country = country
        print re.name
        re.save()
    # elif cells[4] != '':
    #     ci.name = cells[4]    #City name adding (Львів, Paris ..)
