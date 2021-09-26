from django import template

register = template.Library()

@register.filter(name='percentage')
def percentage(value):
    if value is None:
        return None
    if type(value) == str:
        return value
    return '{0:.1%}'.format(float(value))

@register.filter(name='millions')
def millions(value):
    if value is None:
        return None
    if type(value) == str:
        return value
    return '{0:.1f}'.format(float(value/1000000))
