from django import template

register = template.Library()

@register.filter('separate')
def separate(value):
    return [value[i*4: (i+1)*4] for i in range(4)]

@register.filter('first_element')
def first_element(value):
    res = []
    for row in value:
        res.append(row[0])
    return res

@register.filter('abs')
def separate(value):
    return abs(value)