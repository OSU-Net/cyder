from piston.handler import BaseHandler, rc
from systems.models import System, SystemRack,SystemStatus,NetworkAdapter,KeyValue,ServerModel,Allocation
from truth.models import Truth, KeyValue as TruthKeyValue
from dhcp.DHCP import DHCP as DHCPInterface
from dhcp.models import DHCP
from MacroExpansion import MacroExpansion
from KeyValueTree import KeyValueTree
import re
try:
    import json
except:
    from django.utils import simplejson as json
from django.test.client import Client
from django.db.models import Q
from django.conf import settings

class SystemHandler(BaseHandler):
    allowed_methods = settings.API_ACCESS
    model = System
    #fields = ('id', 'asset_tag', 'oob_ip', 'hostname', 'operating_system', ('system_status',('status', 'id')))
    exclude = ()
    def read(self, request, system_id=None):
        model = System
        base = model.objects
        #return base.get(id=453)
        if 'name_search' in request.GET:
            try:
                s = System.objects.filter(hostname__contains=request.GET['name_search'])
            except:
                resp = rc.NOT_FOUND
                return resp
            if s is not None:
                return s
        if 'search' in request.GET:
            search_q = Q()
            has_criteria = False
            systems = None
            if 'asset_tag' in request.GET:
                has_criteria = True
                search_q &= Q(asset_tag=request.GET['asset_tag'])
            if 'serial' in request.GET:
                has_criteria = True
                search_q &= Q(serial=request.GET['serial'])
            if 'rack_order' in request.GET:
                has_criteria = True
                search_q &= Q(rack_order=request.GET['rack_order'])
            if 'switch_ports' in request.GET:
                has_criteria = True
                search_q &= Q(switch_ports=request.GET['switch_ports'])
            if 'system_rack_id' in request.GET:
                has_criteria = True
                try:
                    sr = SystemRack.objects.get(id=request.GET['system_rack_id'])
                    search_q &= Q(system_rack=sr)
                except:
                    pass
            if has_criteria:
                systems = System.with_related.filter(search_q).order_by('hostname')
            if systems is not None and len(systems) > 0:
                return systems
            else:
                resp = rc.NOT_FOUND
                return resp
        elif system_id:
            try:
                try:
                    s = System.objects.get(id=system_id)
                except:
                    pass
                try:
                    s = System.objects.get(hostname=system_id)
                except:
                    pass
                if s is not None:
                    return s
            except:
                resp = rc.NOT_FOUND
                return resp
        else:
            #return base.filter(id_gt=400) # Or base.filter(...)
            return base.all()
    def create(self, request, system_id=None):
        s = System()
        s.hostname = system_id 
        try:
            s.save()
            resp = rc.CREATED
            resp.write('json = {"id":%i, "hostname":"%s"}' % (s.id, s.hostname))
        except:
            resp = rc.BAD_REQUEST
            resp.write('Unable to Create Host')
            
        return resp

    def delete(self, request, system_id=None):
        try:
            try:
                s = System.objects.get(id=system_id)
            except:
                pass
            try:
                s = System.objects.get(hostname=system_id)
            except:
                pass
            id = s.id
            hostname = s.hostname
            s.delete()
            resp = rc.ALL_OK
            resp.write('json = {"id":%i, "hostname":"%s"}' % (id, hostname))
        except:
            resp = rc.NOT_FOUND
            resp.write("Unable to find system")

        return resp
    def update(self, request, system_id=None):
        model = System
    	if request.method == 'PUT':
            try:
                try:
                    s = System.objects.get(id=system_id)
                except:
                    pass
                try:
                    s = System.objects.get(hostname=system_id)
                except:
                    pass
                if 'allocation' in request.POST:
                    try:
                        sa = Allocation.objects.get(id=request.POST['allocation'])
                        s.allocation = sa
                    except Exception, e:
                        pass
                        resp = rc.NOT_FOUND
                        resp.write("Server Not Found %s" % e) 
                if 'server_model' in request.POST:
                    try:
                        sm = ServerModel.objects.get(id=request.POST['server_model'])
                        s.server_model = sm
                    except:
                        pass
                        #resp = rc.NOT_FOUND
                        #resp.write("Server Not Found") 
                if 'system_status' in request.POST:
                    ss = None
                    try:
                        ss = SystemStatus.objects.get(status=request.POST['system_status'])
                        s.system_status = ss
                    except:
                        pass
                    if ss is None:
                        try:
                            ss = SystemStatus.objects.get(id=request.POST['system_status'])
                            s.system_status = ss
                        except:
                            pass
                if 'system_rack' in request.POST:
                    try:
                        sr = SystemRack.objects.get(id=request.POST['system_rack'])
                        s.system_rack = sr
                    except:
                        pass
                        #resp = rc.NOT_FOUND
                        #resp.write("System Rack Not Found") 
                if 'location' in request.POST:
                    s.location = request.POST['location']
                if 'asset_tag' in request.POST:
                    s.asset_tag = request.POST['asset_tag']
                if 'switch_ports' in request.POST:
                    s.switch_ports = request.POST['switch_ports']
                if 'serial' in request.POST:
                    s.serial = request.POST['serial']

                if 'rack_order' in request.POST:
                    s.rack_order = request.POST['rack_order']
                if 'purchase_price' in request.POST:
                    s.purchase_price = request.POST['purchase_price']
                if 'oob_ip' in request.POST:
                    s.oob_ip = request.POST['oob_ip']

                if 'hostname' in request.POST:
                    s.hostname = request.POST['hostname']

                if 'notes' in request.POST:
                    s.notes = request.POST['notes']
                s.save()
                resp = rc.ALL_OK
                resp.write('json = {"id":%i, "hostname":"%s"}' % (s.id, s.hostname))
            except:
                resp = rc.NOT_FOUND
                resp.write("System Updated")
            return resp
