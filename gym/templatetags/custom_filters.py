from django import template

register = template.Library()

@register.filter
def get_range(value):
    return range(value)  # returns a range object based on the integer value

