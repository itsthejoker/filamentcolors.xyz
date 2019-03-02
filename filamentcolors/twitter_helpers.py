import os
import random

from dotenv import load_dotenv

from twitter import Api

load_dotenv()

api = Api(
    consumer_key=os.environ.get('TWITTER_CONSUMER_KEY'),
    consumer_secret=os.environ.get('TWITTER_CONSUMER_SECRET'),
    access_token_key=os.environ.get('TWITTER_ACCESS_TOKEN_KEY'),
    access_token_secret=os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')
)

intro_phrases = [
    'Swatcheriffic!',
    'Just added a new swatch!',
    "What's that I see? A new swatch‽",
    "New swatch ahoy!",
    "A new swatch appears!",
    "More filament!",
    "Another swatch? Another!",
    "Let there be color!",
    "What's this?",
    "More plastic has arrived!",
    "Where'd this come from?",
    "A new swatch!",
    "A new color!",
    "Colors ahoy!",
    "Swatches abound!",
]

outro_phrases = [
    'can be found here:',
    'can be seen here:',
    'joins the library!',
    'now available!',
    'is now available!',
    'now listed!',
    'has been added!',
    'has been added here:',
    'now listed!',
    'is now listed!',
    'is now in the library!',
    'can be found in the library!',
    'appears here:',
    'is listed here:',
]


def send_tweet(swatch):
    plural = "'" if swatch.manufacturer.endswith("s") else "'s"
    api.PostUpdate(
        f'{random.choice(intro_phrases)} {swatch.manufacturer}{plural} {swatch.color_name}'
        f' {swatch.filament_type} {random.choice(outro_phrases)}'
        f' https://filamentcolors.xyz/swatch/{swatch.id}'
    )
