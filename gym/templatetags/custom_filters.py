from django import template

register = template.Library()


@register.filter
def to_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0
    
@register.filter
def get_range(value):
    """
    Returns a range object based on the integer value.
    """
    try:
        return range(int(value))
    except (ValueError, TypeError):
        return range(0)