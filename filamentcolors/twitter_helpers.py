import os
import random
import string

import httpx
from dotenv import load_dotenv
from twitter import Api

load_dotenv()

api = Api(
    consumer_key=os.environ.get("TWITTER_CONSUMER_KEY"),
    consumer_secret=os.environ.get("TWITTER_CONSUMER_SECRET"),
    access_token_key=os.environ.get("TWITTER_ACCESS_TOKEN_KEY"),
    access_token_secret=os.environ.get("TWITTER_ACCESS_TOKEN_SECRET"),
)

REF_KEY = "[[ref]]"

intro_phrases = [
    "Swatcheriffic!",
    "Just added a new swatch!",
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
    "Holy moly!",
    "SWATCH-TALITY!",
    "I found this under the bed!",
    "Just pushed an update!",
    "What do you think of this one?",
    "Can't have enough color!",
    "🚨 New swatch alert! 🚨",
    "Whatchamacallit alert!",
    "Something you might be interested in!",
    "Success!",
    "Hey, check this out!",
    "SWATCHES!",
    "More colors!",
]

outro_phrases = [
    "can be found here:",
    "can be seen here:",
    "joins the library!",
    "now available!",
    "is now available in the library!",
    "now listed!",
    "has been added!",
    "has been added here:",
    "now listed!",
    "is now listed!",
    "is now in the library!",
    "can be found in the library!",
    "appears here:",
    "is listed here:",
    "",
    "is available!",
    "has arrived!",
    "is here!",
]


def generate_swatch_upload_message(swatch) -> str:
    plural = "'" if swatch.manufacturer.name.endswith("s") else "'s"
    return (
        f"{random.choice(intro_phrases)} {swatch.manufacturer.name}{plural}"
        f" {swatch.color_name} {swatch.filament_type.name}"
        f" {random.choice(outro_phrases)}"
        f" https://filamentcolors.xyz/swatch/{swatch.id}?ref={REF_KEY}"
    )


def send_to_social_media(message: str = None, swatch=None) -> None:
    if not message:
        message = generate_swatch_upload_message(swatch)
    # Post to Twitter
    api.PostUpdate(message.replace(REF_KEY, "newswatchtweet"))

    # Post to Mastodon
    httpx.post(
        "https://3dp.chat/api/v1/statuses",
        data={"status": message.replace(REF_KEY, "newswatchtoot")},
        headers={"Authorization": f'Bearer {os.environ.get("MASTODON_ACCESS_TOKEN")}'},
    )


daily_tweet_intro = [
    "There are colors we know and colors we have yet to know!",
    "Let's take a stroll through the archives!",
    "Spin the wheel of random selection to see what we get!",
    "It's always fun to find colors we may not have seen before.",
    "`return random.choice(Swatch.objects.all(published=True))`",
    "A quick scroll through the archives unearthed this!",
    "[insert clickbait intro here]",
    "Remember, filaments in the mirror may be closer than they appear.",
    "This tweet may be automated, but it's more reliable than some printers I've worked on.",
    "Maybe you've seen this one before, maybe you haven't.",
    "Maybe this one's new to you, maybe it's not!",
    "Wanted: 3D-printing-related one-liners to put as intros to these tweets. Apply within.",
    "Pick a color, any color... nevermind, I guessed wrong. But!",
    "The history books pulled this swatch for your perusal.",
    "A website sending its own tweets? That's preposterous. Let's look at swatches instead!",
    "Is it just me or is the interrobang criminally underrated‽ But anyway, back to swatches.",
    "Today's fashion-forward color is brought to you by Python! Python: not just a snake!",
    '"Swatches?! Why does it always have to be swatches???"',
    "🎶 Do you hear the swatches print? Swatches are printing all the time... 🎵",
    "Looking for some new colors? The librarian has some recommendations!",
    "I asked the Magic 8-Ball for your favorite color and it gave me something!",
    "I've always wondered why my copy of Gray's Anatomy is tan... hmm...",
    "🎶 Voulez-vous coloriez avec moi, ce soir? 🎵",
    "If a print fails and no one is around to hear it, does it still spaghetti? Anyway...",
    "Did you see that clip of {famous_person} doing {totally_normal_thing}??? Anyway...",
    "This post is brought to you by the number {number}!",
    "Heeeere's Swatchy!",
    "Fun fact: my bookshelves are (mostly!) organized by color. Ask me about it sometime!",
    "One of these days I'll add a bunch of Sims loading messages. Reticulating splines...",
    "Is it possible to have too many samples? Yes, but actually no.",
    "So I was thinking... how much filament is too much filament? Hrm.",
    "This post is brought to you by the letter {letter}!",
    "Has it been long enough? Can we make fetch happen now?",
    "Roses are red, violets are blue, and we've got swatches of all of them too!",
    "Fun fact: this site is powered by hamsters! Okay, it's actually DigitalOcean, but still.",
    "Fun fact: there are {swatchcount} swatches currently available for your perusal!",
    "Got an idea for one of these messages? Hit me up!",
]


def generate_daily_swatch_tweet(swatch):
    from filamentcolors.models import Swatch  # hooray for no circular imports

    plural = swatch.manufacturer.get_possessive_apostrophe
    intro:str = random.choice(daily_tweet_intro)
    intro = intro.replace("{number}", random.choice(string.digits))
    intro = intro.replace("{letter}", random.choice(string.ascii_uppercase))
    intro = intro.replace("{swatchcount}", str(Swatch.objects.filter(published=True).count()))

    full_update = (
        f"{intro}\n\nHave you seen this one yet? {swatch.manufacturer.name}{plural}"
        f" {swatch.color_name} {swatch.filament_type.name} can be found here:"
        f" https://filamentcolors.xyz/swatch/{swatch.id}?ref=autotweet"
    )

    return full_update
