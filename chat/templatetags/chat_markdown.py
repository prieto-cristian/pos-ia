from django import template
from django.utils.safestring import mark_safe
from markdown_it import MarkdownIt

register = template.Library()

_markdown = MarkdownIt("commonmark", {"html": False, "breaks": True})
_markdown.enable("table")


def _tabla_desplazable(self, tokens, idx, options, env):
    return '<div class="msg-table-scroll" tabindex="0"><table>\n'


def _cierre_tabla(self, tokens, idx, options, env):
    return "</table></div>\n"


_markdown.add_render_rule("table_open", _tabla_desplazable)
_markdown.add_render_rule("table_close", _cierre_tabla)


@register.filter
def markdown_a_html(texto):
    return mark_safe(_markdown.render(texto))
