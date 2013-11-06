from django.db.models.loading import get_model

from cyder.cydns.validation import _name_type_check


def name_to_domain(fqdn):
    """
    This function doesn't throw an exception if nothing is found.
    """
    Domain = get_model('cyder', 'domain')
    _name_type_check(fqdn)
    labels = fqdn.split('.')
    for i in xrange(len(labels)):
        name = '.'.join(labels[i:])
        longest_match = Domain.objects.filter(name=name)
        if longest_match:
            return longest_match[0]
    return None
