from django import template

register = template.Library()


@register.filter
def vnd(value):
    """500000 -> 500.000"""
    try:
        number = int(round(float(value)))
    except (TypeError, ValueError):
        return value
    return f"{number:,}".replace(",", ".")
