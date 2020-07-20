# This can't be in helpers because of a circular import, so it's just easier
# to move it to its own file.
# import mistune
# from mistune.directives import admonition


def bootstrap_render_html_admonition(text, name, title=None):
    html = ''
    if title:
        html += '<h1>' + title + '</h1>\n'
    if text:
        # <p>My Text</p> to just My Text
        try:
            text = text.split("<p>")[1].split("</p>")[0]
        except IndexError:
            pass
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

#
# admonition.render_html_admonition = bootstrap_render_html_admonition
# admonition.Admonition.SUPPORTED_NAMES = {
#     "primary",
#     "secondary",
#     "success",
#     "danger",
#     "warning",
#     "info",
#     "light",
#     "dark"
# }
#
# markdown = mistune.create_markdown(
#     plugins=[
#         admonition.Admonition(),
#         'footnotes',
#         'url',
#         'strikethrough',
#         'table'
#     ]
# )
