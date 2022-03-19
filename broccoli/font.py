from typing import Dict, List, Iterator
from broccoli.glyph import Glyph


class Font:
    def __init__(self, font_name: str, glyphs: Iterator[Glyph]):
        self._font_name = font_name
        self._glyphs = {glyph.name: glyph for glyph in glyphs}

    @property
    def name(self):
        return self._font_name

    def __call__(self, glyph_name: str):
        return self._glyphs[glyph_name]

    def __iter__(self):
        return iter(self._glyphs.keys())

    def __len__(self):
        return len(self._glyphs)
