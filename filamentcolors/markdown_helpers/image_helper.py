import markdown

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

        container = markdown.util.etree.Element("div")
        container.set("class", "text-center photobox")

        outsidelink = markdown.util.etree.Element("a")
        outsidelink.set("href", url)
        outsidelink.set("data-caption", filename)

        img = markdown.util.etree.Element("img")
        img.set("class", "img-fluid rounded")
        img.set("src", url)
        img.set("alt", filename)

        container.append(outsidelink)
        outsidelink.append(img)
        return container


class ImageHelperExtension(markdown.Extension):

    def extendMarkdown(self, md, md_globals):
        # override the built-in `image_link` processor in `markdown.inlinepatterns`
        md.inlinePatterns['image_link'] = ImageHelperPattern(IMAGE_RE, md)


def makeExtension(*args, **kwargs):
    return ImageHelperExtension(*args, **kwargs)
