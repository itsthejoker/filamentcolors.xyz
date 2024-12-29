from django.core.management.base import BaseCommand

from filamentcolors.models import Swatch


class Command(BaseCommand):
    help = "Mark all existing swatches as having been posted to social media"

    def handle(self, *args, **options):
        items = Swatch.objects.filter(posted_to_social_media=False, published=True)
        for item in items:
            item.posted_to_social_media = True
        Swatch.objects.bulk_update(items, ["posted_to_social_media"], batch_size=100)
        self.stdout.write(
            self.style.SUCCESS(
                "All published swatches marked as posted to social media!"
            )
        )
