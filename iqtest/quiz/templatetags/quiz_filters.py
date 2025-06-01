from django import template

register = template.Library()

@register.filter
def get_option_image(queryset, key):
    return queryset.filter(key=key).first()


from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(value, arg):
    return value.as_widget(attrs={'class': arg})