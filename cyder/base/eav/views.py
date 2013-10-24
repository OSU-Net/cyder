from django.http import HttpResponse, Http404

from cyder.base.utils import make_megafilter
from cyder.base.eav.models import Attribute

import json


def search(request):
    """Returns a list of attributes matching 'term'."""
    term = request.GET.get('term', '')
    if not term:
        raise Http404

    attributes = Attribute.objects.filter(
        make_megafilter(Attribute, term))[:15]
    attributes = [{
        'label': str(attribute),
        'pk': attribute.id} for attribute in attributes]
    return HttpResponse(json.dumps(attributes))
