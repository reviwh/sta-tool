import html
import re

from PyQt6.QtGui import QTextFormat


_TAG_RE = re.compile(r"<COLOR=0x([0-9A-Fa-f]{8})>|</COLOR>", re.IGNORECASE)


def _css_color(value):
    value = value.upper()
    red = int(value[0:2], 16)
    green = int(value[2:4], 16)
    blue = int(value[4:6], 16)
    alpha = int(value[6:8], 16) / 255
    return f"rgba({red},{green},{blue},{alpha:.3f})"


def _append_text(parts, text, color):
    if not text:
        return
    escaped = html.escape(text, quote=False).replace("\n", "<br>")
    if color:
        parts.append(f'<span style="color:{_css_color(color)}">{escaped}</span>')
    else:
        parts.append(escaped)


def text_to_html(text):
    """Render ``<COLOR=0xRRGGBBAA>`` tags as rich text spans."""
    parts = []
    stack = []
    position = 0
    for match in _TAG_RE.finditer(text):
        color = stack[-1] if stack else None
        _append_text(parts, text[position:match.start()], color)
        if match.group(1) is not None:
            stack.append(match.group(1))
        elif stack:
            stack.pop()
        position = match.end()
    color = stack[-1] if stack else None
    _append_text(parts, text[position:], color)
    return f'<div style="white-space:pre-wrap">{"".join(parts)}</div>'


def _tag_for_format(char_format):
    color = char_format.foreground().color()
    return (
        f"<COLOR=0x{color.red():02X}{color.green():02X}"
        f"{color.blue():02X}{color.alpha():02X}>"
    )


def document_to_text(document):
    """Rebuild the project string, wrapping colored runs in color tags."""
    pieces = []
    for block_index in range(document.blockCount()):
        if block_index:
            pieces.append("\n")
        block = document.findBlockByNumber(block_index)
        iterator = block.begin()
        while not iterator.atEnd():
            fragment = iterator.fragment()
            chunk = fragment.text().replace("\u2028", "\n").replace("\u2029", "\n")
            char_format = fragment.charFormat()
            if char_format.hasProperty(QTextFormat.Property.ForegroundBrush):
                pieces.append(f"{_tag_for_format(char_format)}{chunk}</COLOR>")
            else:
                pieces.append(chunk)
            iterator += 1
    return "".join(pieces)


def cursor_to_text(cursor):
    """Rebuild only the selected text, wrapping colored runs in color tags."""
    document = cursor.document()
    start = cursor.selectionStart()
    end = cursor.selectionEnd()
    if start >= end:
        return document_to_text(document)

    pieces = []
    for block_index in range(document.blockCount()):
        block = document.findBlockByNumber(block_index)
        block_start = block.position()
        content_end = block_start + block.length() - 1
        sel_start = max(start, block_start)
        sel_end = min(end, content_end)

        if sel_start < sel_end:
            iterator = block.begin()
            while not iterator.atEnd():
                fragment = iterator.fragment()
                fragment_start = fragment.position()
                fragment_end = fragment_start + len(fragment.text())
                from_pos = max(sel_start, fragment_start)
                to_pos = min(sel_end, fragment_end)
                if from_pos < to_pos:
                    chunk = fragment.text()[
                        from_pos - fragment_start : to_pos - fragment_start
                    ]
                    chunk = chunk.replace("\u2028", "\n").replace("\u2029", "\n")
                    char_format = fragment.charFormat()
                    if char_format.hasProperty(
                        QTextFormat.Property.ForegroundBrush
                    ):
                        pieces.append(
                            f"{_tag_for_format(char_format)}{chunk}</COLOR>"
                        )
                    else:
                        pieces.append(chunk)
                iterator += 1

        if (
            start <= content_end < end
            and block_index + 1 < document.blockCount()
        ):
            pieces.append("\n")

    return "".join(pieces)
