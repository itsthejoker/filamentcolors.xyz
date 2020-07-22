import markdown

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

    def handleMatch(self, m):
        classname = m.group(2)
        message = m.group(3)

        container = markdown.util.etree.Element("div")
        container.set("class", "container")

        row = markdown.util.etree.Element("div")
        row.set("class", "row")

        filler_column = markdown.util.etree.Element("div")
        filler_column.set("class", "col-sm-0 col-md-2")

        alert_column = markdown.util.etree.Element("div")
        alert_column.set("class", "col-sm-0 col-md-8")

        alert = markdown.util.etree.Element("div")
        alert.set("class", f"alert alert-{classname} text-center")
        alert.text = markdown.util.AtomicString(message)

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
