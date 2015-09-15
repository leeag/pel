from modeltranslation.translator import translator, TranslationOptions
from models import Country, Region, City


class CountryTranlsationOptions(TranslationOptions):
    fields = ('name', 'region_name',)

translator.register(Country, CountryTranlsationOptions)


class RegionTranlsationOptions(TranslationOptions):
    fields = ('name',)

translator.register(Region, RegionTranlsationOptions)


class CityTranlsationOptions(TranslationOptions):
    fields = ('name',)

translator.register(City, CityTranlsationOptions)

