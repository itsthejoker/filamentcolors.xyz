from django.core.management.base import BaseCommand
from filamentcolors.models import Swatch


class Command(BaseCommand):
    help = "Copy the date_added to date_published for all published swatches"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Beginning process"))
        for s in Swatch.objects.filter(published=True):
            s.date_published = s.date_added
            s.save()
        self.stdout.write(self.style.SUCCESS("Rebuild complete!"))
