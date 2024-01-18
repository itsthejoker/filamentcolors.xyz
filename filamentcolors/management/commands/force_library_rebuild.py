from django.core.management.base import BaseCommand

from filamentcolors.models import Swatch


class Command(BaseCommand):
    help = "Rebuild the related swatch entries for all swatches."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Beginning library rebuild..."))
        for s in Swatch.objects.filter(published=True):
            s.update_all_color_matches(Swatch.objects.filter(published=True))
            s.save()
        self.stdout.write(self.style.SUCCESS("Rebuild complete!"))
