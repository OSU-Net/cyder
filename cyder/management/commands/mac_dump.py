from django.core.management.base import BaseCommand, CommandError

from operator import itemgetter
from optparse import make_option

from cyder.models import StaticInterface, DynamicInterface


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-o', '--output',
                    default=False,
                    help="Direct output to a file"),
    )
    format_str = "{mac} {ctnr} {hostname} More_than_90_days\n"
    used_macs = set()
    forbidden_macs = set(("00:00:00:00:00:00", "ff:ff:ff:ff:ff:ff",))

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
        static = StaticInterface.objects.order_by('mac')
        dynamic = DynamicInterface.objects.order_by('mac')
        interfaces = [
            {
                'mac': si.mac,
                'ctnr': si.ctnr.name,
                'hostname': si.system.name,
            }
            for si in static if self.use_mac(si.mac)
        ] + [
            {
                'mac': di.mac,
                'ctnr': di.ctnr.name,
                'hostname': di.system.name,
            }
            for di in dynamic if self.use_mac(di.mac)
        ]

        # sort by mac
        interfaces = sorted(interfaces, key=itemgetter('mac'))

        output = ""

        for i in interfaces:
            output += self.format_str.format(**i)

        if options['output']:
            # output to a file
            f = open(options['output'], 'w')
            f.write(output)
            f.close()
        else:
            print output