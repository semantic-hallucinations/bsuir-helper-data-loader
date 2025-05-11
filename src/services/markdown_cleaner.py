from typing import List

import mistune


class TextRenderer(mistune.HTMLRenderer):
    def text(self, text):
        return text

    def paragraph(self, text):
        return text

    def heading(self, text, level):
        return text

    def list(self, body, ordered, depth=None, start=None):
        return body

    def list_item(self, text):
        return text

    def link(self, text, url, title=None):
        return text

    def table(self, content):
        return content

    def table_row(self, content):
        return content

    def table_cell(self, content, header=False, align=None):
        return content + " | "

    def strong(self, text):
        return text

    def emphasis(self, text):
        return text


class StructuredRenderer(mistune.HTMLRenderer):
    def text(self, text):
        return text

    def paragraph(self, text):
        return text + "\n"

    def heading(self, text, level):
        return text

    def list(self, body, ordered, depth=None, start=None):
        items = body.split("\n")
        marker = f"{start}." if ordered and start else "1." if ordered else "-"
        return "\n".join(f"{marker} {item}" for item in items if item.strip())

    def list_item(self, text):
        return text

    def link(self, text, url, title=None):
        return f"[{text}]({url})"

    def table(self, content):
        return content.rstrip("\n")

    def table_row(self, content):
        return content + "\n"

    def table_cell(self, content, header=False, align=None):
        return content + " | "

    def strong(self, text):
        return text

    def emphasis(self, text):
        return text

    def html_tag(self, tag, text, attrs):
        return text


async def clean_markdown_for_saving(md_texts: List[str]) -> List[str]:
    renderer = StructuredRenderer()
    md_parser = mistune.Markdown(renderer=renderer)
    return [md_parser(md_text).strip() for md_text in md_texts]


async def clean_markdown_for_embeddings(md_texts: List[str]) -> List[str]:
    renderer = TextRenderer()
    md_parser = mistune.Markdown(renderer=renderer)
    return [md_parser(md_text).strip() for md_text in md_texts]
