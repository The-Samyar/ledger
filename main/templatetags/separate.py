from django import template

register = template.Library()

@register.filter('separate')
def separate(value):
    return [value[i*4: (i+1)*4] for i in range(4)]