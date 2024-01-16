import os
import random
import string

import httpx
from django.urls import reverse
from dotenv import load_dotenv

from filamentcolors import tumblr as pytumblr

load_dotenv()

tumblr = pytumblr.TumblrRestClient(
    os.environ.get("TUMBLR_CONSUMER_KEY"),
    os.environ.get("TUMBLR_SECRET"),
    os.environ.get("TUMBLR_OAUTH_TOKEN"),
    os.environ.get("TUMBLR_OAUTH_TOKEN_SECRET"),
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


def send_to_social_media(message: str = None, swatch=None, new_swatch=False) -> None:
    if not message and not swatch:
        raise Exception("Cannot create posts without either a message or a swatch!")
    if not message:
        message = generate_swatch_upload_message(swatch)

    try:
        # Post to Mastodon
        httpx.post(
            "https://3dp.chat/api/v1/statuses",
            data={
                "status": message.replace(
                    REF_KEY, "newswatchtoot" if new_swatch else "autotoot"
                )
            },
            headers={
                "Authorization": f'Bearer {os.environ.get("MASTODON_ACCESS_TOKEN")}'
            },
        )
    except Exception as e:
        print(e)

    try:
        # Post to Tumblr

        # first fix the post message to remove the url, since it isn't clickable
        # by default on tumblr
        if new_swatch:
            tumblr_message = message.split(" https://")[0]
        else:
            split_message = message.split("here:")
            tumblr_message = split_message[0] + "at filamentcolors.xyz!"

        tumblr.create_photo(
            "filamentcolors.tumblr.com",
            state="published",
            tags=[
                "3d printing",
                "3d print",
                "project",
                "projects",
                "colors",
                "color inspo",
                "maker",
                "making",
            ],
            caption=tumblr_message,
            format="markdown",
            link="https://filamentcolors.xyz"
            + reverse("swatchdetail", kwargs={"id": swatch.id})
            + f"?ref={'newswatchtumbl' if new_swatch else 'autotumbl'}",
            data=swatch.image_front.path,
        )
    except Exception as e:
        print(e)


daily_tweet_intro = [
    "There are colors we know and colors we have yet to know!",
    "Let's take a stroll through the archives!",
    "Spin the wheel of random selection to see what we get!",
    "It's always fun to find colors we may not have seen before.",
    "`return random.choice(Swatch.objects.all(published=True))`",
    "A quick scroll through the archives unearthed this!",
    "[insert clickbait intro here]",
    "Remember, filaments in the mirror may be closer than they appear.",
    "This post may be automated, but it's more reliable than some printers I've worked on.",
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


def generate_daily_swatch_message(swatch):
    from filamentcolors.models import Swatch  # hooray for no circular imports

    plural = swatch.manufacturer.get_possessive_apostrophe
    intro: str = random.choice(daily_tweet_intro)
    intro = intro.replace("{number}", random.choice(string.digits))
    intro = intro.replace("{letter}", random.choice(string.ascii_uppercase))
    intro = intro.replace(
        "{swatchcount}", str(Swatch.objects.filter(published=True).count())
    )

    full_update = (
        f"{intro}\n\nHave you seen this one yet? {swatch.manufacturer.name}{plural}"
        f" {swatch.color_name} {swatch.filament_type.name} can be found here:"
        f" https://filamentcolors.xyz/swatch/{swatch.id}?ref={REF_KEY}"
    )

    return full_update
