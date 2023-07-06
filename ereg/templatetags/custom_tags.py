from datetime import timedelta
from django import template

register = template.Library()

@register.filter
def add_days(value, days):
    return value + timedelta(days=days)

@register.filter
def format_date(value, arg):
    return value.strftime(arg)

@register.filter
def add_days(value, days):
    return value + timedelta(days=days)

@register.filter
def add(value, arg):
    return value + arg

from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, {})



@register.filter
def get_i(l, key):
    return l[key]
