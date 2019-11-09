from django.core.management.base import BaseCommand, CommandError
from filamentcolors.models import GenericFilamentType


class Command(BaseCommand):
    help = 'Creates the base types used for navigation'

    def handle(self, *args, **options):
        TYPES = [
            'PLA',
            'PETG',
            'ABS',
            'TPU / TPE',
            'Exotics'
        ]

        created_types = list()

        for t in TYPES:
            check = GenericFilamentType.objects.filter(name=t).first()
            if not check:
                GenericFilamentType.objects.create(name=t)
                created_types.append(t)

        if len(created_types) == 0:
            self.stdout.write(
                self.style.SUCCESS('No types created; all present.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    'Created the following types: {}'.format(
                        ', '.join(created_types)
                    )
                )
            )
