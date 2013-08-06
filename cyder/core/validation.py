from django.core.exceptions import ValidationError

import string

ALLOWED_CTNR_NAME = string.digits + string.ascii_letters + ".-_"


def validate_ctnr_name(name):
    for char in name:
        if char not in ALLOWED_CTNR_NAME:
            raise ValidationError(
                "Character '{0}' not allowed in container names.".format(char))
