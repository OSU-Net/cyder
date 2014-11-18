# encoding: utf_8


from django.core.exceptions import ValidationError


def validate_positive_integer_field(val):
    if not val <= 4294967295:
        raise ValidationError(
            u'Value must be within the range 0 – 4294967295.')


def validate_integer_field(val):
    if not -2147483648 <= val <= 2147483647:
        raise ValidationError(
            u'Value must be within the range -2147483648 – 2147483647.')
