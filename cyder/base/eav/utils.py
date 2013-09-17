import re
from django.core.exceptions import ValidationError


default_validator = lambda x: x != '' # FIXME: Do we need this?

def validate_list(value, validator=default_validator, separator=',',
                  strip_whitespace=True, min_length=0, die=False):
    """Validate a "list" of things
    separator: the char that separates list items (None means whitespace)
    allow_whitespace: whether to strip whitespace around separators before
                      validating (unnecessary if separator is None)

    Returns whether validator returned True for every item in value. Note that
    this is not terribly useful.
    """

    items = value.split(separator)
    length = len(items)

    all_valid = all([validator(x.strip() if strip_whitespace else x)
                     for x in items])

    if not all_valid:
        if die:
            raise ValidationError("One or more list items are invalid")
        else:
            return False
    elif length < min_length:
        if die:
            raise ValidationError("List must contain at least {0} items"
                                  .format(length))
        else:
            return False
    else:
        return True


def is_hex_byte(value):
    return bool(re.match(r'^[0-9a-fA-F]{2}$', value))


def is_hex_byte_sequence(value):
    return validate_list(value, _hex_byte, separator=':',
                         strip_whitespace=False)


def strip_and_get_base(value):
    if value[0:2] == '0x':
        value = value[2:]
        base = 16
    else:
        base = 10
    return (value, base)
