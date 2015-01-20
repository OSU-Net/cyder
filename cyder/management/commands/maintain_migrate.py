from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db.models.loading import get_model


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('-q', '--qlobber',
                    action='store_true',
                    dest='qlobber',
                    default=False,
                    help='Clobber the Maintain sandbox'),
        make_option('-t', '--together',
                    action='store_true',
                    dest='together',
                    default=False,
                    help='Migrate DNS and DHCP objects together efficiently'),
        make_option('-d', '--dns',
                    action='store_true',
                    dest='dns',
                    default=False,
                    help='Migrate DNS objects'),
        make_option('-p', '--dhcp',
                    action='store_true',
                    dest='dhcp',
                    default=False,
                    help='Migrate DHCP objects'))

    def handle(self, **options):
        if options['qlobber']:
            print "Clobbering Maintain sandbox."

            from .lib import maintain_dump
            maintain_dump.main()
            from .lib import fix_maintain
            fix_maintain.main()

        if options['together']:
            from . import dhcp_migrate, dns_migrate
            options['dns'], options['dhcp'] = False, False
            dns_migrate.delete_DNS()
            dns_migrate.delete_CNAME()
            dhcp_migrate.delete_all()
            dns_migrate.gen_domains_only()
            dhcp_migrate.migrate_zones()
            dhcp_migrate.migrate_zone_reverse()
            dhcp_migrate.migrate_vlans()
            dhcp_migrate.migrate_workgroups()
            dhcp_migrate.migrate_subnets()
            dhcp_migrate.migrate_ranges()
            dhcp_migrate.migrate_zone_range()
            dhcp_migrate.migrate_zone_workgroup()
            dhcp_migrate.migrate_zone_domain()
            dns_migrate.gen_DNS(skip_edu=False)
            dns_migrate.gen_CNAME()
            dhcp_migrate.migrate_dynamic_hosts()
            dhcp_migrate.migrate_user()
            dhcp_migrate.migrate_zone_user()

            print 'Updating range usage.'
            Range = get_model('cyder', 'range')
            ranges = Range.objects.all()
            for rng in ranges:
                rng.save()

            print "Scheduling SOA rebuilds."
            SOA = get_model('cyder', 'soa')
            for s in SOA.objects.all():
                s.schedule_rebuild(save=True, force=True)

        if options['dns']:
            print "Migrating DNS objects."
            dns_migrate.do_everything(skip_edu=False)

        if options['dhcp']:
            dhcp_migrate.do_everything(skip=False)

        del options['verbosity']
        del options['settings']
        if not any(options.values()):
            raise CommandError("No flags passed; no action taken. "
                               "Try maintain_migrate --help")
