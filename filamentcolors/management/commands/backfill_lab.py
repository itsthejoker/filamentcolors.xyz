from django.core.management.base import BaseCommand

from filamentcolors.models import Swatch


class Command(BaseCommand):
    # For anyone who may find this: yes, I know that this is inaccurate.
    # This is step one of converting the library to function entirely on
    # LAB color instead of RGB.
    # We will eventually finish scanning the entire library again to bring
    # it properly into the LAB color space... but we still need something
    # to work against in the meantime.
    help = "Backfill the LAB color space for all swatches using existing color data."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Beginning LAB backfill..."))
        library = Swatch.objects.filter(hex_color__isnull=False)
        self.stdout.write("Swatches to backfill: {}".format(library.count()))
        for swatch in library:
            if swatch.hex_color == "":
                continue
            swatch._set_lab_from_rgb()
            swatch.computed_lab = True
            swatch.save()
        self.stdout.write(self.style.SUCCESS("Backfill complete!"))
