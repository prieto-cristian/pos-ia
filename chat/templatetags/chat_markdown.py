from django import template
from django.utils.safestring import mark_safe
from markdown_it import MarkdownIt

register = template.Library()

_markdown = MarkdownIt("commonmark", {"html": False, "breaks": True})


@register.filter
def markdown_a_html(texto):
    return mark_safe(_markdown.render(texto))
