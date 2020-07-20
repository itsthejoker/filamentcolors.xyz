import mistune
from mistune.directives import admonition

admonition_keywords = {
    "primary",
    "secondary",
    "success",
    "danger",
    "warning",
    "info",
    "light",
    "dark"
}


def bootstrap_render_html_admonition(text, name, title=None):
    html = ''
    if title:
        html += '<h1>' + title + '</h1>\n'
    if text:
        html += (
                '<div class="row">\n<div class="col-sm-0 col-md-4"></div>\n'
                '<div class="col-sm-12 col-md-4">\n'
                f'<div class="alert alert-{name} text-center">'
                + text +
                "</div>\n"
                "</div>\n"
                '<div class="col-sm-0 col-md-4"></div>\n'
                "</div>"
        )
    return html


admonition.render_html_admonition = bootstrap_render_html_admonition
admonition.Admonition.SUPPORTED_NAMES = admonition_keywords

markdown = mistune.create_markdown(
    plugins=[
        admonition.Admonition(),
        'footnotes',
        'url',
        'strikethrough',
        'table'
    ]
)
with open('test.md') as f:
    print(markdown(f.read()))
