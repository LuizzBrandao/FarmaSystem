from django import template

register = template.Library()

@register.filter
def abs_value(value):
    """Retorna o valor absoluto de um número"""
    try:
        return abs(int(value))
    except (ValueError, TypeError):
        return 0

@register.filter
def multiply(value, arg):
    """Multiplica um valor por outro"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def subtract(value, arg):
    """Subtrai um valor de outro"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0
