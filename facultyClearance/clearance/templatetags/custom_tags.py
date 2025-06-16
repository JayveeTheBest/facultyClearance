import os
from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def replace(value, arg):
    """Replaces all values of arg[0] with arg[1] in the given string."""
    old, new = arg.split(',')
    return value.replace(old, new)


@register.filter
def basename(value):
    """Returns the base name of a file path."""
    print(f"[DEBUG] Raw value in basename: {value}")
    return os.path.basename(str(value))
