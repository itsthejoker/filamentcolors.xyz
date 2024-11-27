####
# Site Banner Message
#
# Set to `None` if we don't want a message to display. Otherwise, just fill in the data.
# If someone clicks the 'X' button, it will hide that particular banner message forever
# until a different message (with a different ID) is created.
####

from hashlib import md5

# a string that will be displayed in full at the top of the site. Can contain html.
NAVBAR_MESSAGE: str | None = (
    "Hey there - please take a moment to read <a href='https://forum.filamentcolors.xyz/d/10-looking-forward-whats-next-funding' class='alert-link text-white'>our message about the future of the site here.</a>"
)
# an ID for the 'don't show' cookie. Unique per message.
NAVBAR_MESSAGE_ID: str | None = (
    md5(NAVBAR_MESSAGE.encode("utf-8")).hexdigest() if NAVBAR_MESSAGE else None
)
