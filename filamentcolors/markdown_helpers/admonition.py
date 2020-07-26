import markdown
from markdown.util import AtomicString
from xml.etree.ElementTree import Element, SubElement
from xml import etree
import regex
import re

# I can't quite get multiline working, but this is a start:
# r'(?m)^(?:[ ]{4,}|\t+)*(WARNING|INFO) *\w+ .*(?:[\r\n]^([ ]{2,}|\t+)[^\s].*)*'
ADMONITION_RE = r'::(primary|secondary|success|danger|warning|info|light|dark)[ ]{1}(.*)'


class AdmonitionPattern(markdown.inlinepatterns.Pattern):
    """
    Format a message into a bootstrap banner.

    For now, it must be a single line. That will hopefully change once I get
    the regex figured out.

    Usage:

    ::primary Hey, this is a message!

    ::danger This may not work the way you expect it to and it may screw up your day
    """

    """
    '<div class="row">\n
    <div class="col-sm-0 col-md-4"></div>\n'
    '<div class="col-sm-12 col-md-4">\n'
    f'<div class="alert alert-{name} text-center">'
    + text +
    "</div>\n"
    "</div>\n"
    '<div class="col-sm-0 col-md-4"></div>\n'
    "</div>"
    """

    def build_alert(self, classname, message):
        """
        Because an alert can have links in it, this is exponentially more
        complicated than it seems like it should be. Normally we can just
        build the alert and call it a day, but if there are any links in
        the message then we have to intelligently build the formatting
        for each link and place them into the message in the right places.

        This was a pain in the butt to get working and I hope it never breaks.
        """
        alert = Element("div")
        alert.set("class", f"alert alert-{classname} text-center")

        # ripped wholesale from the markdown package because it uses re instead
        # of regex, and regex can't use re-compiled regex
        STX = '\u0002'  # Use STX ("Start of text") for start-of-placeholder
        ETX = '\u0003'  # Use ETX ("End of text") for end-of-placeholder
        INLINE_PLACEHOLDER_PREFIX = STX + "klzzwxh:"
        INLINE_PLACEHOLDER = INLINE_PLACEHOLDER_PREFIX + "%s" + ETX
        INLINE_PLACEHOLDER_RE = regex.compile(INLINE_PLACEHOLDER % r'([0-9]+)')

        link_matches = [i for i in regex.finditer(INLINE_PLACEHOLDER_RE, message)]
        if len(link_matches) == 0:
            alert.text = AtomicString(message)
            return alert

        # start with up to the beginning of the first link
        alert.text = AtomicString(message[:link_matches[0].start()])
        # python markdown stashes away things that it can't process immediately.
        # The problem comes when we try to modify strings that have stashed
        # nodes in them, which for some reason completely breaks Markdown's
        # ability to recall / reinstate those stashed nodes. That means
        # that we have to do the whole damn process ourselves.
        # tl;dr: perform a lot of string slicing to insert links in the right
        # spots so that everything works.
        stash = self.md.treeprocessors['inline'].stashed_nodes
        prev = None
        for link in link_matches:
            if prev:
                prev[0].tail = AtomicString(message[prev[1].end(): link.start()])
            mylink = stash[link.group(1)]
            link_alert = SubElement(alert, "a")
            link_alert.set("href", mylink.get('href'))
            link_alert.set('class', 'alert-link')
            link_alert.set("target", "_blank")

            link_alert.text = AtomicString(mylink.text)
            # group them together so we can use them on the next
            # iteration if we have more than one link
            prev = (link_alert, link)

        # Now that we're done with the loop, link_alert should be the last link
        # that was created.
        link_alert.tail = AtomicString(message[link.end():])
        return alert


    def handleMatch(self, m):
        classname = m.group(2)
        message = m.group(3)

        container = Element("div")
        container.set("class", "container")

        row = Element("div")
        row.set("class", "row")

        filler_column = Element("div")
        filler_column.set("class", "col-sm-0 col-md-2")

        alert_column = Element("div")
        alert_column.set("class", "col-sm-0 col-md-8")

        alert = self.build_alert(classname, message)

        container.append(row)
        row.append(filler_column)
        row.append(alert_column)
        alert_column.append(alert)
        row.append(filler_column)

        # underline = markdown.util.etree.Element("u")
        # el = markdown.util.etree.Element("a")
        # el.set('href', message)
        # el.text = markdown.util.AtomicString()
        # underline.append(el)
        return container


class AdmonitionExtension(markdown.Extension):
    """ Urlize Extension for Python-Markdown. """

    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns['admonition'] = AdmonitionPattern(ADMONITION_RE, md)


def makeExtension(*args, **kwargs):
    return AdmonitionExtension(*args, **kwargs)
