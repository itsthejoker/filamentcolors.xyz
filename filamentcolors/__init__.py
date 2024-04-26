####
# Site Banner Message
#
# Set to `None` if we don't want a message to display. Otherwise, just fill in the data.
# If someone clicks the 'X' button, it will hide that particular banner message forever
# until a different message (with a different ID) is created.
####

# a string that will be displayed in full at the top of the site. Can contain html.
NAVBAR_MESSAGE: str | bool = None
# an ID for the 'don't show' cookie. Use a string of a UUID4.
NAVBAR_MESSAGE_ID: str | bool = None