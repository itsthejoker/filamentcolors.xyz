import random

from django.conf import settings
from django.core.management.base import BaseCommand

from filamentcolors.models import Swatch
from filamentcolors.social_media import send_to_social_media


class Command(BaseCommand):
    help = "Mark all existing swatches as having been posted to social media"

    def handle(self, *args, **options):
        unposted_swatches = Swatch.objects.filter(
            posted_to_social_media=False, published=True
        )
        if unposted_swatches.count() == 0:
            return

        item = random.choice(unposted_swatches)
        item.posted_to_social_media = True
        if settings.POST_TO_SOCIAL_MEDIA:
            send_to_social_media(swatch=item, new_swatch=True)
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Posting disabled. Would have posted {item} to social media"
                )
            )
        item.save()
