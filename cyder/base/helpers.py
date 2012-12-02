# Jingo helpers (Jinja2 custom filters)
import json

from jingo import register


@register.filter
def humanized_class_name(obj, *args, **kwargs):
    """
    Adds spaces to camel-case class names.
    """
    humanized = ''

    class_name = obj.__class__.__name__

    for i in range(len(class_name)):
        humanized += class_name[i]
        # Insert space between every camel hump.
        if (i + 1 < len(class_name) and class_name[i].islower()
            and class_name[i + 1].isupper()):
            humanized += ' '

    return humanized

@register.filter
def prettify_record_type(record_type, *args, **kwargs):
    """
    Turns all-lowercase record type string to all caps or splits into
    words if underscore.
    e.g. 'cname' to 'CNAME' and 'address_record' to 'Address Record'
    """
    if not record_type:
        return

    prettified = ''

    if record_type == 'domain':
        return 'Domain'
    elif record_type == 'nameserver':
        return 'Nameserver'
    elif '_' in record_type:
        capitalize = True
        for i in range(len(record_type)):
            if capitalize:
                prettified += record_type[i].upper()
                capitalize = False
            elif record_type[i] == '_':
                prettified += ' '
                capitalize = True
            else:
                prettified += record_type[i]
        return prettified

    return record_type.upper()


@register.function
def a_or_an(next_word):
    """
    Chooses 'a' or 'an' depending on first letter of next word.
    Add in special cases if next word is 'hour' or something.
    """
    if next_word[0] in ['a', 'e', 'i', 'o', 'u']:
        return 'an'
    else:
        return 'a'


@register.function
def has_attr(obj, attr):
    return hasattr(obj, attr)


@register.filter
def to_json(obj):
    """Object to JSON."""
    return json.dumps(obj)
