from django.core.management.base import BaseCommand

from filamentcolors.models import Swatch


class Command(BaseCommand):
    help = "Generate opengraph images for all swatches"

    def handle(self, *args, **options):
        for swatch in Swatch.objects.filter(
            published=True, image_opengraph__isnull=True
        ):
            swatch.create_opengraph_image(close_django_file_too=True)
            swatch.save()
            self.stdout.write(f"Generated opengraph image for {swatch.id}")
        self.stdout.write(self.style.SUCCESS("All done!"))
