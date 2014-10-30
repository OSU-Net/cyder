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


def is_name_descendant_of(name1, name2):
    """Returns True if name1 is a descendant of name2, False otherwise."""

    from itertools import izip_longest

    for s, o in izip_longest(reversed(name1), reversed(name2),
            fillvalue='!'):
        if s == '!':  # self is shorter.
            return False
        if o == '!':  # other is shorter.
            if s == '.':  # self matches and has more labels.
                return True
            else:  # self doesn't match (it has extra bytes in this label).
                return False
        if s != o:  # self doesn't match other (a byte differs).
            return False
    # The names are identical.
    return False
