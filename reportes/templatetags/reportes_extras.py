from django import template

from reportes.utils import dash as dash_value, yn as yn_value


register = template.Library()


@register.filter(name="dash")
def dash_filter(value):
	return dash_value(value)


@register.filter(name="yn")
def yn_filter(value):
	return yn_value(value)
