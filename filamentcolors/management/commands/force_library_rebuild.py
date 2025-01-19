from django.core.management.base import BaseCommand

from filamentcolors.models import Swatch


class Command(BaseCommand):
    help = "Rebuild the related swatch entries for all swatches."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Beginning library rebuild..."))
        for swatch in Swatch.objects.filter(published=True):
            swatch.update_all_color_matches(
                Swatch.objects.filter(published=True), include_third_party=True
            )
            swatch.save()
        self.stdout.write(self.style.SUCCESS("Rebuild complete!"))
