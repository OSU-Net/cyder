from django.core.exceptions import ValidationError


def validate_views(cleaned_data):
    for view in cleaned_data.get('views'):
        if cleaned_data.get('domain'):
            check_no_ns_soa_condition(cleaned_data['domain'], view=view)
        if cleaned_data.get('reverse_domain'):
            check_no_ns_soa_condition(cleaned_data['reverse_domain'],
                                      view=view)


def check_no_ns_soa_condition(domain, view=None):
    if domain.soa:
        fail = False
        root_domain = domain.soa.root_domain
        if root_domain and not root_domain.nameserver_set.exists():
            fail = True
        elif (view and
              not root_domain.nameserver_set.filter(views=view).exists()):
            fail = True
        if fail:
            if view:
                error = '{0} view in {1}'.format(view, domain.name)
            else:
                error = 'domain: {0}'.format(domain.name)
            raise ValidationError(
                "The {0} you are trying to assign this record into does "
                "not have an NS record, thus cannot support other "
                "records.".format(error))
