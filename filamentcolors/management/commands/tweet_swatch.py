import random
from time import sleep

from django.core.management.base import BaseCommand
from django.utils import timezone

from filamentcolors.models import Swatch
from filamentcolors.twitter_helpers import generate_daily_swatch_tweet, send_tweet


def get_random_swatch() -> Swatch:
    return random.choice(
        [s for s in Swatch.objects.filter(published=True) if s.is_available()]
    )


def get_tweet_content(swatch_of_the_day) -> str:
    while True:
        tweet_content = generate_daily_swatch_tweet(swatch_of_the_day)
        if len(tweet_content) < 280:
            # most of these come in around 180 characters, but there are
            # some swatches with long names that blow way past that
            return tweet_content


class Command(BaseCommand):
    help = "Send a tweet about a random swatch in the library."

    def handle(self, *args, **options):
        today = timezone.now().isoweekday()
        if today not in [2, 4, 7]:  # tuesday, thursday, sunday
            # we don't want to run every day... just enough to spice things
            # up a little.
            self.stdout.write("Not the right day... not sending the tweet.")
            return

        # Don't want it to feel too robotic...
        sleep_count = random.choice(range(7200))  # two hour window
        self.stdout.write(f"Sleeping for {sleep_count}")
        sleep(sleep_count)

        send_tweet(get_tweet_content(get_random_swatch()))
