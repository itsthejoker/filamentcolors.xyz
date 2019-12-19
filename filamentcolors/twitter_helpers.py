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
    "A new color!",
    "Gadzooks!",
]

outro_phrases = [
    'can be found here:',
    'can be seen here:',
    'joins the library!',
    'now available!',
    'is now available in the library!',
    'now listed!',
    'has been added!',
    'has been added here:',
    'now listed!',
    'is now listed!',
    'is now in the library!',
    'can be found in the library!',
    'appears here:',
    'is listed here:',
    ''
]


def send_tweet(swatch):
    plural = "'" if swatch.manufacturer.name.endswith("s") else "'s"
    api.PostUpdate(
        f'{random.choice(intro_phrases)} {swatch.manufacturer.name}{plural}'
        f' {swatch.color_name} {swatch.filament_type.name}'
        f' {random.choice(outro_phrases)}'
        f' https://filamentcolors.xyz/swatch/{swatch.id}'
    )


daily_tweet_intro = [
    "There are colors we know and colors we have yet to know!",
    "Let's take a stroll through the archives.",
    "Spin the wheel of random selection to see what we get!",
    "It's always fun to find colors we may not have seen before.",
    "`return random.choice(Swatch.objects.all())`",
    "A quick scroll through the archives unearthed this!",
    "[insert clickbait intro here]",
    "Remember, filaments in the mirror may be closer than they appear.",
    "This tweet may be automated, but at least it's more reliable than some printers I've worked on.",
    "Maybe you've seen this one before, maybe you haven't.",
    "Maybe this one's new to you, maybe it's not!",
    "Wanted: 3D-printing-related one-liners to put as intros to these tweets. Apply within.",
    "Pick a color, any color... nevermind, I guessed wrong. But!",
    "",
    "The history books pulled this swatch for your perusal.",
    "A website sending its own tweets? That's preposterous. Let's look at swatches instead!",
    "Is it just me or is the interrobang criminally underrated‽ But anyway, back to swatches."
]


def send_daily_swatch_tweet(swatch):
    plural = "'" if swatch.manufacturer.name.endswith("s") else "'s"
    api.PostUpdate(
        f'{random.choice(daily_tweet_intro)} Have you seen this one yet? {swatch.manufacturer.name}{plural}'
        f' {swatch.color_name} {swatch.filament_type.name} can be found here:'
        f' https://filamentcolors.xyz/swatch/{swatch.id}'
    )
