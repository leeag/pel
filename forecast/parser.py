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


country = 'name'
region = 'name'
for row in content:

    cells = row.split(',')
    print row
    if cells[0]:
        print 'country'
        #print 'adsadsa'
        global country
        country = cells[0]
        c = Country()
        c.name = cells[0]

        c.save()


    if cells[1]:
        print 'region'

        global region
        region = cells[1]
        r = Region()
        r.name = cells[1]
        rc = Country.objects.get(name_en=country)
        r.country = rc
        r.save()

    if cells[4]:
        print country
        print 'city'
        print cells[4]
        city = City()
        city.name = cells[4]

        city.region = Region.objects.get(name_en=region)
        city.country = Country.objects.get(name_en=country)
        city.save()
    if cells[6] and cells[6]!='\n':
        print 'smt'
        print country
        print cells
        city = City()
        city.name = cells[6]
        city.region = Region.objects.get(name_en=region)
        city.country = Country.objects.get(name_en=country)
        city.save()
