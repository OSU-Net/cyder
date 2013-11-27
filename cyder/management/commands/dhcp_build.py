from cyder.cydhcp.build.builder import build
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-p', '--push',
                    dest='push',
                    action='store_true',
                    default=False,
                    help="Check files into vcs and push upstream."),
        make_option('-C', '--no-sanity-check',
                    dest='sanity_check',
                    action='store_false',
                    default=True,
                    help="Don't run the diff sanity check."),
    )

    def handle_noargs(self, **options):
        with DHCPBuilder(push=option['push']) as b:
            b.build()
            if options['push']:
                b.push(sanity_check=options['sanity_check'])
