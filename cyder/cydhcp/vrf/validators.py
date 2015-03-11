from django.core.exceptions import ValidationError


def validate_vrf_name(name):
    for c in name:
        if not ('A' <= c <= 'Z' or 'a' <= c <= 'z' or '0' <= c <= '9' or
                c in '-_'):
            raise ValidationError(
                'VRF name can only contain letters, numbers, hyphens, and '
                'underscores')
