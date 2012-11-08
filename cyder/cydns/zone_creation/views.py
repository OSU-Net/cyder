from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Q
from django.http import QueryDict
from django.forms.util import ErrorList, ErrorDict
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.http import Http404

from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.address_record.forms import AddressRecordFQDNForm
from cyder.cydns.address_record.forms import AddressRecordForm
from cyder.cydns.ptr.models import PTR
from cyder.cydns.ptr.forms import PTRForm
from cyder.cydns.srv.models import SRV
from cyder.cydns.srv.forms import SRVForm, FQDNSRVForm
from cyder.cydns.txt.models import TXT
from cyder.cydns.txt.forms import TXTForm, FQDNTXTForm
from cyder.cydns.mx.models import MX
from cyder.cydns.mx.forms import MXForm, FQDNMXForm
from cyder.cydns.cname.models import CNAME
from cyder.cydns.cname.forms import CNAMEFQDNForm, CNAMEForm
from cyder.cydns.soa.models import SOA
from cyder.cydns.soa.forms import SOAForm
from cyder.cydns.domain.models import Domain
from cyder.cydns.view.models import View
from cyder.cydns.utils import ensure_label_domain
from cyder.cydns.utils import prune_tree
import operator

from gettext import gettext as _, ngettext
import simplejson as json


def zone_creation(request):
    return render(request, 'zone_creation/zone_creation.html', {})
