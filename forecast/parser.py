# -*- coding: utf-8 -*-
import os
import sys
import django

sys.path.append(r'/home/aspire/PycharmProjects/Peleus/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'Peleus.settings'
django.setup()

from forecast.models import Country, Region, City

with open('countries_regions_cities.csv') as f:
    content = f.readlines()[:20]

co = Country()
re = Region()
ci = City()

for row in content:
    cells = row.split(',')
    if cells[0] != '':
        co.name_en = cells[0]    #Country name adding (Україна, Polska..)
        co.save()
    # elif cells[1] != '':
    #     re.name_en = cells[1]    #Region name adding (Львівська, Małopolskie ..)
    # elif cells[4] != '':
    #     ci.name_en = cells[4]    #City name adding (Львів, Paris ..)
