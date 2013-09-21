from django.core.exceptions import ValidationError

from cyder.cydhcp.constants import STATIC
from cyder.cydhcp.range.models import Range


def is_dynamic_range(r_id):
    r = Range.objects.get(pk=r_id)
    if r and r.range_type == STATIC:
        raise ValidationError('A dynamic interface cannot be in a static '
                              'range.')
