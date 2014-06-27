"""
This management command recreates the functionality of internal script called
radius-report, which produces a file containing all of the MAC addresses (and
associated information) stored in Maintain.
"""
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

import itertools
from operator import itemgetter
from optparse import make_option

from cyder.models import StaticInterface, DynamicInterface


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-f', '--file',
                    default=False,
                    help="If this option is specified, the command's output "
                         "will be written to the given file."),
    )
    other_id_ctnrs = {"zone.public", "zone.resnet", "zone.flexnetoregonstate"}
    output_format = "{mac} {ctnr} {hostname} {modified}\n"
    used_macs = set()
    forbidden_macs = {"", "00:00:00:00:00:00", "ff:ff:ff:ff:ff:ff"}

    def use_mac(self, mac):
        """
        Used to enforce distinct MAC addresses, as well as remove bad MAC
        addresses.
        :param mac: A given interface's MAC address.
        :return: True if the MAC is unique, False if it has already been used.
        """
        if mac in self.used_macs or mac in self.forbidden_macs:
            return False
        else:
            self.used_macs.add(mac)
            return True

    def handle(self, *args, **options):
        # get all unique mac addresses
        static_interfaces = StaticInterface.objects.only(
            'mac', 'ctnr', 'system', 'modified', 'dhcp_enabled')
        dynamic_interfaces = DynamicInterface.objects.only(
            'mac', 'ctnr', 'system', 'modified', 'dhcp_enabled')

        interfaces = []
        for interface in itertools.chain(static_interfaces, dynamic_interfaces):
            if self.use_mac(interface.mac) and interface.dhcp_enabled:
                ctnr = interface.ctnr.name
                system = interface.system

                # handle when the zone name should be the Other ID
                if ctnr in self.other_id_ctnrs:
                    try:
                        other_id = system.systemav_set.get(
                            attribute__name__exact="Other ID").value
                    except ObjectDoesNotExist:
                        other_id = "No_other_id"
                else:
                    other_id = None

                interface_data = {
                    'mac': interface.mac.replace(':', ''),
                    'ctnr': other_id or ctnr,
                    'hostname': system.name,
                    'modified': interface.modified.strftime(
                        # Format to match: Tue Jun  3 10:33:57 2014
                        "%a %b %d %X %Y") if interface.modified
                                          else "More_than_90_days",
                }
                interfaces.append(interface_data)

        # sort by mac
        interfaces = sorted(interfaces, key=itemgetter('mac'))

        output = ""

        for i in interfaces:
            output += self.output_format.format(**i)

        if options['file']:
            # output to a file
            f = open(options['file'], 'w')
            f.write(output)
            f.close()
        else:
            print output