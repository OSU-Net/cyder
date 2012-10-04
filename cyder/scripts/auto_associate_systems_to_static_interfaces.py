#!/usr/bin/python
import sys
import os
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))
import manage
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings.base'
import manage
from cyder.core.range.models import Range, RangeKeyValue
from cyder.core.interface.static_intr.models import StaticInterface
from cyder.mozdns.address_record.models import AddressRecord
from django.db.models import Q
from cyder.core.range.forms import RangeForm
from cyder.mozdns.view.models import View
from cyder.core.range.models import Range, RangeKeyValue
from cyder.core.interface.static_intr.models import StaticInterface
from cyder.mozdns.address_record.models import AddressRecord
from cyder.mozdns.ptr.models import PTR
from cyder.mozdns.ip.models import ipv6_to_longs
from cyder.core.views import CoreDeleteView, CoreDetailView
from cyder.core.views import CoreCreateView, CoreUpdateView, CoreListView
from cyder.core.keyvalue.utils import get_attrs, update_attrs, get_aa, get_docstrings
from cyder.core.keyvalue.utils import get_docstrings, dict_to_kv
import ipaddr
import simplejson as json
from cyder.systems.models import System, KeyValue
from cyder.core.interface.static_intr.views import do_combine_a_ptr_to_interface
from django.test import Client
from cyder.systems.models import System
#(addr, ptr, system, mac_address):


def main():
    for mrange in Range.objects.all():
        #if not str(mrange.network.site) == 'Phx1':
        #    continue
        print "Now starting on Range %s" % mrange
        attrs = mrange.rangekeyvalue_set.all()

        start_upper, start_lower = mrange.start_upper, mrange.start_lower
        end_upper, end_lower = mrange.end_upper, mrange.end_lower

        gt_start = Q(ip_upper=start_upper, ip_lower__gte=start_lower)
        gt_start = gt_start | Q(ip_upper__gte=start_upper)

        lt_end = Q(ip_upper=end_upper, ip_lower__lte=end_lower)
        lt_end = lt_end | Q(ip_upper__lte=end_upper)

        records = AddressRecord.objects.filter(gt_start, lt_end)
        ptrs = PTR.objects.filter(gt_start, lt_end)
        intrs = StaticInterface.objects.filter(gt_start, lt_end)

        range_data = []
        for i in range((start_upper << 64) + start_lower, (end_upper << 64) +
                       end_lower - 1):
            taken = False
            adr_taken = None
            ip_str = str(ipaddr.IPv4Address(i))
            for record in records:
                if record.ip_lower == i:
                    adr_taken = record
                    break

            ptr_taken = None
            for ptr in ptrs:
                if ptr.ip_lower == i:
                    ptr_taken = ptr
                    break

            if ptr_taken and adr_taken:
                if ptr_taken.name == adr_taken.fqdn:
                    range_data.append(('A/PTR', ip_str, ptr_taken, adr_taken))
                else:
                    range_data.append(('PTR', ip_str, ptr_taken))
                    range_data.append(('A', ip_str, adr_taken))
                taken = True
            elif ptr_taken and not adr_taken:
                range_data.append(('PTR', ip_str, ptr_taken))
                taken = True
            elif not ptr_taken and adr_taken:
                range_data.append(('A', ip_str, adr_taken))
                taken = True

            for intr in intrs:
                if intr.ip_lower == i:
                    range_data.append(('Interface', ip_str, intr))
                    taken = True
                    break

            if taken == False:
                range_data.append((None, ip_str))
        client = Client()
        for bl in range_data:
            system_hostname = ''
            try:
                if bl[2].name:
                    #import pdb; pdb.set_trace()
                    intr_hostname = bl[2].name.replace(".mozilla.com", "")
                    system_hostname = intr_hostname
                #system = System.objects.get(hostname=intr_hostname)
                system = KeyValue.objects.filter(
                    key__icontains='ipv4_address', value=bl[1])[0].system
                addr = AddressRecord.objects.get(pk=bl[3].pk)
                ptr = PTR.objects.get(pk=bl[2].pk)
                try:
                    first = True
                    while system.get_next_key_value_adapter():
                        adapter = system.get_next_key_value_adapter()
                        mac_address = adapter['mac_address']
                        num = adapter['num']
                        private = View.objects.get(name='private')
                        if 'nic' in adapter['name'] or 'eth' in adapter['name']:
                            interface = 'eth%s.0' % num
                        elif 'mgmt' in adapter['name']:
                            interface = 'mgmt%s.0' % num
                        else:
                            interface = 'eth%s.0' % num

                        if 'dhcp_hostname' in adapter:
                            dhcp_hostname = adapter['dhcp_hostname']
                        else:
                            dhcp_hostname = None

                        if 'dhcp_filename' in adapter:
                            dhcp_filename = adapter['dhcp_filename']
                        else:
                            dhcp_filename = None

                        if 'dhcp_domain_name_servers' in adapter:
                            dhcp_domain_name_servers = adapter[
                                'dhcp_domain_name_servers']
                        else:
                            dhcp_domain_name_servers = None

                        if 'dhcp_domain_name' in adapter:
                            dhcp_domain_name = adapter['dhcp_domain_name']
                        else:
                            dhcp_domain_name = None

                        if first:
                            intr, addr_del, ptr_del = do_combine_a_ptr_to_interface(
                                addr, ptr, system, mac_address,
                                interface, dhcp_hostname=dhcp_hostname,
                                dhcp_domain_name_servers=dhcp_domain_name_servers,
                                dhcp_domain_name=dhcp_domain_name, dhcp_filename=dhcp_filename)
                            intr.views.add(private)
                            intr.save()
                        else:
                            from cyder.api_v3.system_api import SystemResource
                            intr = StaticInterface(
                                label=addr.label, mac=mac_address, domain=addr.domain,
                                ip_str=addr.ip_str, ip_type=addr.ip_type, system=system)
                            intr.full_clean()
                            intr.dns_enabled = False
                            intr.dhcp_enabled = True
                            intr.save()
                            intr.update_attrs()
                            adapter_type, primary, alias = SystemResource.extract_nic_attrs(interface)
                            intr.attrs.primary = primary
                            intr.attrs.alias = alias
                            intr.attrs.interface_type = adapter_type

                        system.delete_key_value_adapter_by_index(num)
                        first = False
                        print "SUCCESS ===== %s" % system.hostname
                except IndexError:
                    ### We can't get the next adapter
                    pass
                except Exception, e:
                    print e
                    print "FAIL ===== %s - Could not get mac_address for" % system.hostname
                #client.post('/en-US/core/interface/combine_a_ptr_to_interface/%i/%i/' % (bl[3].pk, bl[2].pk), data={'is_ajax' : 1, 'system_hostname': bl[2].name.replace(".mozilla.com", "")})
            except IndexError, e:
                pass
            except System.DoesNotExist, e:
                print "FAIL ===== %s Host Not Found" % (system_hostname)
            except AttributeError, e:
                if str(e) == "'AddressRecord' object has no attribute 'name'":
                    #import pdb; pdb.set_trace()
                    try:
                        print "FAIL ===== %s - %s - %s" % (
                            addr.ip_str, system_hostname, e)
                    except:
                        print "FAIL =====  %s - %s" % (system_hostname, e)
            except Exception, e:
                print "FAIL ===== %s - %s" % (system_hostname, e)
if __name__ == '__main__':
    main()
