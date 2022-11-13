import markdown
from django.conf import settings

"""
This is incompatible with the original `mention` plugin, but it borrows heavily from
the original and functions similarly.
The original use case is represented below.

>>> import markdown
>>> md = markdown.Markdown(extensions=['martor.utils.extensions.twitter_mention'])
>>> md.convert('@[summonagus]')
'<p><a class="direct-mention-link" href="https://webname.com/profile/summonagus/">summonagus</a></p>'
>>>
>>> md.convert('hello @[summonagus], i mentioned you!')
'<p>hello <a class="direct-mention-link" href="https://webname.com/profile/summonagus/">summonagus</a>, i mentioned you!</p>'
>>>
"""

MENTION_RE = r"(?<!\!)\@\[([^\]]+)\]"


class TwitterMentionPattern(markdown.inlinepatterns.Pattern):
    def handleMatch(self, m):
        username = self.unescape(m.group(2))

        """Make sure `username` is registered and active."""
        if settings.MARTOR_ENABLE_CONFIGS["mention"] == "true":
            url = "{0}{1}/".format(settings.MARTOR_MARKDOWN_BASE_MENTION_URL, username)
            el = markdown.util.etree.Element("a")
            el.set("href", url)
            el.set("class", "direct-mention-link")
            underline = markdown.util.etree.Element("u")
            underline.text = markdown.util.AtomicString("@" + username)
            el.append(underline)
            return el


class MentionExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        """Setup `mention_link` with MentionPattern"""
        md.inlinePatterns["mention_link"] = TwitterMentionPattern(MENTION_RE, md)


def makeExtension(*args, **kwargs):
    return MentionExtension(*args, **kwargs)
