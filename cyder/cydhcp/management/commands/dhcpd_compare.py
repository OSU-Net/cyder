from cyder.migration.management.commands.lib.dhcpd_compare.parser \
        import compare

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    args = 'file1 file2'

    def handle(self, *args, **options):
        if len(args) != 2:
            raise CommandError('You must provide two files to compare')

        compare(args[0], args[1])
