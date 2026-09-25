from django import template

register = template.Library()

@register.filter(name='indian_format')
def indian_format(number):
    """
    Formats a number into Indian Standard numbering format (e.g. 1,000 or 4,28,950.00).
    """
    if number is None:
        return '0'
    try:
        val = float(number)
    except (ValueError, TypeError):
        return number

    s = f"{val:.2f}"
    parts = s.split('.')
    integer_part = parts[0]
    decimal_part = parts[1]

    if len(integer_part) <= 3:
        formatted_int = integer_part
    else:
        last_three = integer_part[-3:]
        remaining = integer_part[:-3]
        groups = []
        while len(remaining) > 2:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            groups.insert(0, remaining)
        formatted_int = ','.join(groups) + ',' + last_three

    if decimal_part == '00':
        return formatted_int
    return f"{formatted_int}.{decimal_part}"
