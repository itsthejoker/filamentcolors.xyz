from django.core.management.base import BaseCommand
from filamentcolors.twitter_helpers import generate_daily_swatch_tweet, send_tweet
import random
from django.db.models import Max
from django.utils import timezone
from filamentcolors.models import Swatch


def get_random_swatch() -> Swatch:
    max_id = Swatch.objects.all().aggregate(max_id=Max("id"))['max_id']
    while True:
        try:
            new_id = random.choice(range(1, max_id))
            the_chosen_swatch = Swatch.objects.get(id=new_id)
            if the_chosen_swatch:
                return the_chosen_swatch
        except Swatch.DoesNotExist:
            pass


def get_tweet_content(swatch_of_the_day) -> str:
    while True:
        tweet_content = generate_daily_swatch_tweet(swatch_of_the_day)
        if len(tweet_content) < 280:
            # most of these come in around 180 characters, but there are
            # some swatches with long names that blow way past that
            return tweet_content


class Command(BaseCommand):
    help = 'Send a tweet about a random swatch in the library.'

    def handle(self, *args, **options):
        today = timezone.now().isoweekday()
        if today not in [2, 4, 7]:  # tuesday, thursday, sunday
            # we don't want to run every day... just enough to spice things
            # up a little.
            self.stdout.write("Not the right day... not sending the tweet.")
            return
        send_tweet(get_tweet_content(get_random_swatch()))





