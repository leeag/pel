from django.template.defaulttags import register
from django.contrib.humanize.templatetags.humanize import intcomma


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


# @register.filter
# def currency(dollars):
#     dollars = round(float(dollars), 2)
#     return "$%s%s" % (intcomma(int(dollars)), ("%0.2f" % dollars)[-3:])