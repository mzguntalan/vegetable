from itertools import tee, chain, repeat

from fontTools.ttLib import TTFont
from xml.etree import ElementTree
from typing import Iterable, Optional, List
from pathlib import Path
from os.path import isabs
from broccoli.glyph import Glyph
from broccoli.font import Font
from broccoli.ttf.ttglyph import Point, Contour
from carrot.vector_graphic import VectorGraphic
from carrot.svg import Line, QuadraticCurve
import os.path
from functools import reduce


class TTFReader:
    def __init__(
        self,
        glyph_names_to_read_in_font_files: Iterable,
        num_points_for_approximation: int,
    ):
        self._glyph_names = glyph_names_to_read_in_font_files
        self._num_points_for_approximation = num_points_for_approximation

    def read_font(
        self,
        path_to_ttf_font_file: str,
        path_to_save_temporary_files_that_will_get_deleted_after_reading: str = "../tmp",
    ) -> Font:
        path_to_ttf_font_file = Path(path_to_ttf_font_file)
        font_name = path_to_ttf_font_file.parts[-1].replace(".ttf", "")

        path_to_temporary = Path(
            path_to_save_temporary_files_that_will_get_deleted_after_reading
        )

        path_to_temporary = (
            path_to_temporary
            if isabs(path_to_temporary)
            else path_to_ttf_font_file.parent / path_to_temporary
        )

        if not os.path.exists(path_to_temporary):
            os.makedirs(path_to_temporary)

        path_to_temporary /= font_name + ".xml"

        font = TTFont(path_to_ttf_font_file)
        font.saveXML(path_to_temporary)

        font_xml = ElementTree.parse(path_to_temporary)

        return self._get_font_from_glyphs(
            font_name, self._get_glyphs_from_font_xml(font_xml)
        )

    def _get_font_from_glyphs(self, font_name: str, glyphs: Iterable[Glyph]) -> Font:
        return Font(font_name, glyphs)

    def _get_glyphs_from_font_xml(self, font_xml: ElementTree) -> Iterable[Glyph]:
        root_of_xml = font_xml.getroot()
        ttglyphs = root_of_xml.findall("glyf")[0].findall("TTGlyph")

        # get_glyph_from_ttglyph = lambda ttglyph: Glyph(
        #     glyph_name=get_name_of_ttglyph(ttglyph),
        #     vector_graphic_of_the_glyph=sum(
        #         map(
        #             lambda contour: self._get_vector_graphic_from_contour(contour),
        #             map(get_contour_from_ttcontour, get_ttcontours_of_ttglyph(ttglyph)),
        #         )
        #     ),
        # )

        desired_ttglyphs = filter(
            lambda g: self._get_name_of_ttglyph(g) in self._glyph_names, ttglyphs
        )
        return map(lambda g: self._get_glyph_from_ttglyph(g), desired_ttglyphs)

    def _get_name_of_ttglyph(self, ttglyph):
        return ttglyph.attrib["name"]

    def _get_glyph_from_ttglyph(self, ttglyph):
        get_ttcontours_of_ttglyph = lambda g: g.findall("contour")
        get_ttpoints_in_ttcontour = lambda ttcontour: ttcontour.findall("pt")
        get_point_from_ttpoint_bounded_by_min_and_max = (
            lambda ttpoint, min_x, max_x, min_y, max_y: Point(
                x=max(min(float(ttpoint.attrib["x"]), max_x), min_x),
                y=max(min(float(ttpoint.attrib["y"]), max_y), min_y),
                h=float(ttpoint.attrib["on"]),
            )
        )
        # get_contour_from_points = lambda points: Contour(points)

        get_contour_from_ttcontour = lambda ttcontour: Contour(
            map(
                get_point_from_ttpoint_bounded_by_min_and_max,
                get_ttpoints_in_ttcontour(ttcontour),
                repeat(-10_000),
                repeat(10_000),
                repeat(-10_000),
                repeat(10_000),
            )
        )

        glyph_name = self._get_name_of_ttglyph(ttglyph)
        ttcontours = get_ttcontours_of_ttglyph(ttglyph)
        contours = map(get_contour_from_ttcontour, ttcontours)
        vector_graphics = map(
            lambda c: self._get_vector_graphic_from_contour(c), contours
        )
        vg = reduce(lambda vg_0, vg_1: vg_0 + vg_1, vector_graphics)
        return Glyph(glyph_name=glyph_name, vector_graphic_of_the_glyph=vg)

    def _get_vector_graphic_from_contour(self, contour: Contour) -> VectorGraphic:
        vg = self._get_vector_graphic_sequence_from_point_sequence(
            contour.point_sequence
        )
        vg, vg2 = tee(vg)
        vg2 = list(vg2)
        s = vg2[0]
        for v in vg2[1:]:
            s += v

        return reduce(lambda vg_0, vg_1: vg_0 + vg_1, vg)

    def _get_vector_graphic_sequence_from_point_sequence(
        self,
        point_sequence: Iterable[Point],
        vector_graphic_sequence: Iterable[VectorGraphic] = (),
        points_read: Iterable[Point] = (),
    ) -> Iterable:
        point_sequence = iter(point_sequence)
        points_read = iter(points_read)
        incoming_point = next(point_sequence, None)
        if incoming_point is None:
            return vector_graphic_sequence

        last_point_read = next(points_read, None)
        if last_point_read is None:
            return self._get_vector_graphic_sequence_from_point_sequence(
                point_sequence, vector_graphic_sequence, iter([incoming_point])
            )

        if incoming_point.is_on() and last_point_read.is_on():
            vector_graphic = Line(
                start_point=last_point_read.get_as_xy_tuple(),
                end_point=incoming_point.get_as_xy_tuple(),
                num_points_for_approximation=self._num_points_for_approximation,
            )
            points_read = iter([incoming_point, last_point_read])
        elif incoming_point.is_on() and last_point_read.is_off():
            second_to_last_point_read = next(
                points_read
            )  # the last point couldn't be the first point because off point are not allowed to be first
            # second to last point also assured to be on, because of ttx rules
            vector_graphic = QuadraticCurve(
                start_point=second_to_last_point_read.get_as_xy_tuple(),
                end_point=incoming_point.get_as_xy_tuple(),
                control_point=last_point_read.get_as_xy_tuple(),
                num_points_for_approximation=self._num_points_for_approximation,
            )
            points_read = iter(
                [incoming_point, last_point_read, second_to_last_point_read]
            )
        elif incoming_point.is_off() and last_point_read.is_on():
            second_incoming_point = next(point_sequence)
            vector_graphic = QuadraticCurve(
                start_point=last_point_read.get_as_xy_tuple(),
                end_point=second_incoming_point.get_as_xy_tuple(),
                control_point=incoming_point.get_as_xy_tuple(),
                num_points_for_approximation=self._num_points_for_approximation,
            )
            points_read = iter([second_incoming_point, incoming_point, last_point_read])
        else:
            raise RuntimeError("TTX did not follow rules.")
        return self._get_vector_graphic_sequence_from_point_sequence(
            point_sequence,
            chain(vector_graphic_sequence, iter([vector_graphic])),
            points_read,
        )
        #
        # if last_point_used_for_building_last_vector_graphic is None:
        #     second_incoming_point = next(point_sequence, None)
        #     last_incoming_point = second_incoming_point
        #     if second_incoming_point is None:
        #         raise ValueError(
        #             "Point sequence contains a point that belongs to no group."
        #         )
        #
        #     if second_incoming_point.is_off():
        #         third_incoming_point = next(point_sequence)
        #         last_incoming_point = third_incoming_point
        #
        #         vector_graphic = QuadraticCurve(
        #             start_point=incoming_point.get_as_xy_tuple(),
        #             end_point=third_incoming_point.get_as_xy_tuple(),
        #             control_point=second_incoming_point.get_as_xy_tuple(),
        #             num_points_for_approximation=self._num_points_for_approximation,
        #         )
        #     else:
        #         vector_graphic = Line(
        #             start_point=incoming_point.get_as_xy_tuple(),
        #             end_point=second_incoming_point.get_as_xy_tuple(),
        #             num_points_for_approximation=self._num_points_for_approximation,
        #         )
        #
        #     return self._get_vector_graphic_sequence_from_point_sequence(
        #         point_sequence,
        #         chain(vector_graphic_sequence, iter([vector_graphic])),
        #         last_point_used_for_building_last_vector_graphic=last_incoming_point,
        #     )
