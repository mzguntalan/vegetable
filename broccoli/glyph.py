from carrot.vector_graphic import VectorGraphic
from typing import List, Optional, Iterator


class Glyph(VectorGraphic):
    def __init__(
        self,
        glyph_name: str,
        vector_graphic_of_the_glyph: Optional[VectorGraphic] = None,
        sequence_of_segments_that_make_up_the_glyph: Optional[
            Iterator[VectorGraphic]
        ] = None,
    ):
        if (
            vector_graphic_of_the_glyph is None
            and sequence_of_segments_that_make_up_the_glyph is None
        ) or (
            vector_graphic_of_the_glyph is not None
            and sequence_of_segments_that_make_up_the_glyph is not None
        ):
            raise ValueError(
                "Please specify exactly one of vector_graphic_of_the_glyph or sequence_of_segments."
            )

        if sequence_of_segments_that_make_up_the_glyph is not None:
            vector_graphic_of_the_glyph = sum(
                sequence_of_segments_that_make_up_the_glyph
            )

        super().__init__(
            vector_graphic_of_the_glyph._start_point,
            vector_graphic_of_the_glyph._end_point,
            f_portion_s=vector_graphic_of_the_glyph._f_portion_s,
            num_points_for_approximation=vector_graphic_of_the_glyph.num_points_for_approximation,
        )

        self._glyph_name = glyph_name

    @property
    def name(self):
        return self._glyph_name
