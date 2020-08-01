import markdown
from markdown.util import AtomicString
from xml.etree.ElementTree import Element

IMAGE_RE = r'!\[(.*)]\((.*)\)'


class ImageHelperPattern(markdown.inlinepatterns.Pattern):
    """Catch and reformat image links for bootstrap"""

    """
    <div class="text-center">
        <a href="img/1-1.jpg" data-caption="Golden Gate Bridge">
            <img src="img/thumbs/1-1.jpg" alt="Golden Gate Bridge">
        </a>
    </div>
    
    <img src="..." class="rounded" alt="...">
    
    """

    def handleMatch(self, m):
        filename = m.group(2)
        url = m.group(3)

        container = Element("div")
        container.set("class", "container")

        row = Element("div")
        row.set("class", "row")

        filler_column = Element("div")
        filler_column.set("class", "col-sm-0 col-md-2")

        picture_column = Element("div")
        picture_column.set("class", "col-sm-0 col-md-8")

        picture_container = Element("div")
        picture_container.set("class", "text-center")

        outsidelink = Element("a")
        outsidelink.set("href", url)
        outsidelink.set("data-caption", filename)

        img = Element("img")
        img.set("class", "img-fluid border rounded postImg")
        img.set("src", url)
        img.set("alt", filename)

        clickme_container = Element("div")
        clickme = Element("small")
        clickme.text = AtomicString("Click for full-sized image")
        clickme.set("class", "text-muted")
        clickme_container.append(clickme)

        outsidelink.append(img)
        outsidelink.append(clickme_container)
        picture_container.append(outsidelink)
        picture_column.append(picture_container)

        container.append(row)
        row.append(filler_column)
        row.append(picture_column)
        row.append(filler_column)

        return container


class ImageHelperExtension(markdown.Extension):

    def extendMarkdown(self, md, md_globals):
        # override the built-in `image_link` processor in `markdown.inlinepatterns`
        md.inlinePatterns['image_link'] = ImageHelperPattern(IMAGE_RE, md)


def makeExtension(*args, **kwargs):
    return ImageHelperExtension(*args, **kwargs)
