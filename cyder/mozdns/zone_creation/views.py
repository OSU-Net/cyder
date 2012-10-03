from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Q
from django.http import QueryDict
from django.forms.util import ErrorList, ErrorDict
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.http import Http404

from cyder.mozdns.address_record.models import AddressRecord
from cyder.mozdns.address_record.forms import AddressRecordFQDNForm
from cyder.mozdns.address_record.forms import AddressRecordForm
from cyder.mozdns.ptr.models import PTR
from cyder.mozdns.ptr.forms import PTRForm
from cyder.mozdns.srv.models import SRV
from cyder.mozdns.srv.forms import SRVForm, FQDNSRVForm
from cyder.mozdns.txt.models import TXT
from cyder.mozdns.txt.forms import TXTForm, FQDNTXTForm
from cyder.mozdns.mx.models import MX
from cyder.mozdns.mx.forms import MXForm, FQDNMXForm
from cyder.mozdns.cname.models import CNAME
from cyder.mozdns.cname.forms import CNAMEFQDNForm, CNAMEForm
from cyder.mozdns.soa.models import SOA
from cyder.mozdns.soa.forms import SOAForm
from cyder.mozdns.domain.models import Domain
from cyder.mozdns.view.models import View
from cyder.mozdns.utils import ensure_label_domain
from cyder.mozdns.utils import prune_tree
import operator

from gettext import gettext as _, ngettext
import simplejson as json
import pdb


def zone_creation(request):
    return render(request, 'zone_creation/zone_creation.html', {})
