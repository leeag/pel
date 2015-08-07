from django.template.defaulttags import register
from django.contrib.humanize.templatetags.humanize import intcomma


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)