"""
Note: keeping this file named `tweet_swatch` so that I don't have to rename
the cron job.
"""

import random
from time import sleep

from django.core.management.base import BaseCommand
from django.utils import timezone

from filamentcolors.models import Swatch
from filamentcolors.social_media import (
    generate_daily_swatch_message,
    send_to_social_media,
)


def get_random_swatch() -> Swatch:
    return random.choice(
        [s for s in Swatch.objects.filter(published=True) if s.is_available()]
    )


def get_update_content(swatch_of_the_day) -> str:
    while True:
        content = generate_daily_swatch_message(swatch_of_the_day)
        if len(content) < 280:
            # most of these come in around 180 characters, but there are
            # some swatches with long names that blow way past that
            return content


class Command(BaseCommand):
    help = "Send an update about a random swatch in the library."

    def handle(self, *args, **options):
        today = timezone.now().isoweekday()
        if today not in [2, 4, 7]:  # tuesday, thursday, sunday
            # we don't want to run every day... just enough to spice things
            # up a little.
            self.stdout.write("Not the right day... not sending the update.")
            return

        # Don't want it to feel too robotic...
        sleep_count = random.choice(range(7200))  # two-hour window
        self.stdout.write(f"Sleeping for {sleep_count}")
        sleep(sleep_count)

        swatch_to_post = get_random_swatch()

        send_to_social_media(
            message=get_update_content(swatch_to_post), swatch=swatch_to_post
        )
