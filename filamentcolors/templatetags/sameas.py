# -*- coding: utf-8 -*-

#
# This file is part of Django-SameAs.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program.  If not, see
# <http://www.gnu.org/licenses/>.
#
# Copyright (C) 2013 by 4web.bg
#

# original repo: https://github.com/ydm/django-sameas

from __future__ import unicode_literals
from django import template
from django.template.loader_tags import BlockNode, do_block


register = template.Library()


_block_key = lambda b: "__sameas_{}__".format(b)


class SameNode(template.Node):
    def __init__(self, block_name):
        self.block_name = block_name

    def render(self, context):
        return context[_block_key(self.block_name)].render(context)


@register.tag("sameas")
def do_sameas(parser, token):
    try:
        tag, block = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "{} tag requires a single argument".format(token.split_contents()[0])
        )
    else:
        return SameNode(block)


# ydm: I have to override the default `block` tag handler since
# there's no other way (as far as I know) to access block's rendered
# content
class BlockNodeProxy(BlockNode):
    def __init__(self, name, nodelist, parent=None):
        super(BlockNodeProxy, self).__init__(name, nodelist)

    def render(self, context):
        result = super(BlockNodeProxy, self).render(context)
        if _block_key(self.name) not in context:
            context[_block_key(self.name)] = self
        return result


@register.tag("block")
def modified_do_block(parser, token):
    node = do_block(parser, token)
    return BlockNodeProxy(node.name, node.nodelist)
