from django.core.management.base import BaseCommand, CommandError
from cyder.dnsutils.dns_build import zone_build_from_config


class Command(BaseCommand):
    args = ''

    def handle(self, *args, **options):
        if len(args) != 1:
            print "Jobs are: external, dc, private_reverse"
            return
        print args
        zone_build_from_config(job=args[0])
