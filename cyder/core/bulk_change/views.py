from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.shortcuts import render
from django.contrib import messages
from django.forms.util import ErrorList
from django.http import HttpResponse

from cyder.systems.models import System

from cyder.core.interface.static_intr.models import StaticInterface
from cyder.core.interface.static_intr.models import StaticIntrKeyValue
from cyder.core.interface.static_intr.forms import StaticInterfaceForm
from cyder.core.interface.static_intr.forms import FullStaticInterfaceForm
from cyder.core.interface.static_intr.forms import StaticInterfaceQuickForm
from cyder.core.interface.static_intr.forms import CombineForm
from cyder.core.keyvalue.utils import get_attrs, update_attrs, get_aa, get_docstrings
from cyder.core.keyvalue.utils import get_docstrings, dict_to_kv
from cyder.core.views import CoreDeleteView, CoreCreateView
from cyder.core.range.models import Range
from cyder.core.network.utils import calc_parent_str

from cyder.mozdns.domain.models import Domain
from cyder.mozdns.address_record.models import AddressRecord
from cyder.mozdns.ptr.models import PTR

from cyder.core.search.parser import parse
from cyder.core.search.search import compile_search

import pdb
import re
import ipaddr
import operator
import simplejson as json


from jinja2 import Environment, PackageLoader
env = Environment(loader=PackageLoader('core.bulk_change', 'templates'))


def bulk_change_ajax(request):
    search = request.GET.get("search", None)
    if not search:
        return HttpResponse("What do you want?!?")
    query = parse(search)
    print "----------------------"
    print query
    print "----------------------"

    x = compile_search(query)
    addrs, cnames, domains, intrs, mxs, nss, ptrs, srvs, txts, misc = x
    template = env.get_template('bulk_change/bulk_change_form_content.html')
    return HttpResponse(template.render(
        **{
        "search": search,
        "addrs": addrs,
        "cnames": cnames,
        "intrs": intrs,
        "mxs": mxs,
        "nss": nss,
        "ptrs": ptrs,
        "srvs": srvs,
        "txts": txts
        }
    ))


def bulk_change(request):
    """Search page"""
    search = request.GET.get('search', '')
    return render(request, "bulk_change/bulk_change.html", {
        "search": search
    })
