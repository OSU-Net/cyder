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
    output_format = "{mac} {zone_identifier} {hostname} {modified}\n"
    # prefill bad MAC's so only good MAC's get added to the access point
    used_macs = {"", "00:00:00:00:00:00", "ff:ff:ff:ff:ff:ff"}

    def use_mac(self, mac):
        """
        Used to enforce distinct MAC addresses, as well as remove bad MAC
        addresses.
        :param mac: A given interface's MAC address.
        :return: True if the MAC is unique, False if it has already been used.
        """
        if mac in self.used_macs:
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
            if not (interface.dhcp_enabled and self.use_mac(interface.mac)):
                continue

            zone_identifier = interface.ctnr.name
            system = interface.system

            # For certain special case ctnrs, the zone_identifier field should
            # be the device's Other ID instead of a ctnr name.
            if zone_identifier in self.other_id_ctnrs:
                try:
                    zone_identifier = system.systemav_set.get(
                        attribute__name__exact="Other ID").value
                except ObjectDoesNotExist:
                    zone_identifier = "No_other_id"

            interface_data = {
                'mac': interface.mac.replace(':', ''),
                'zone_identifier': zone_identifier,
                'hostname': system.name,
                'modified': interface.modified.strftime("%a %b %d %X %Y"),
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