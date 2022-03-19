from typing import List, Optional, Tuple, Iterator
from itertools import chain


class Point:
    def __init__(self, x, y, h):
        self.x = x
        self.y = y
        self.h = h

    def is_on(self) -> bool:
        return self.h == 1

    def is_off(self) -> bool:
        return not self.is_on()

    def get_as_xy_tuple(self) -> Tuple[float, float]:
        return (self.x, self.y)

    def __add__(self, other) -> "Point":
        return Point(x=self.x + other.x, y=self.y + other.y, h=1)

    def __truediv__(self, other) -> "Point":
        assert isinstance(other, int) or isinstance(other, float)
        return Point(x=self.x / other, y=self.y / other, h=self.h)

    def __repr__(self):
        return str((self.x, self.y, self.h))

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.h == other.h


class Contour:
    def __init__(self, point_sequence: Iterator[Point]):
        self._point_sequence = self._decompress(point_sequence)

    @property
    def point_sequence(self) -> Iterator[Point]:
        return iter(self._point_sequence)

    def _decompress(self, point_sequence: Iterator[Point]) -> Iterator[Point]:
        return self._remove_off_off_sequence_of_points_by_putting_an_on_point_in_between_them(
            self._fix_end_points(point_sequence)
        )

    def _fix_end_points(self, point_sequence: Iterator[Point]) -> Iterator[Point]:
        point_sequence = list(point_sequence)
        first_point, last_point = point_sequence[0], point_sequence[-1]

        if first_point.is_off():
            if last_point.is_on():
                point_sequence = [last_point] + point_sequence
            else:
                virtual_point_in_between = (first_point + last_point) / 2
                point_sequence = (
                    [virtual_point_in_between]
                    + point_sequence
                    + [virtual_point_in_between]
                )
        else:
            if last_point.is_off():
                point_sequence = point_sequence + [first_point]

        first_point, last_point = point_sequence[0], point_sequence[-1]
        if last_point != first_point:
            point_sequence = point_sequence + [first_point]

        return iter(point_sequence)

    def _remove_off_off_sequence_of_points_by_putting_an_on_point_in_between_them(
        self,
        point_sequence: Iterator[Point],
        sequence_with_no_successive_off_points: Iterator[Point] = iter([]),
        last_point_added: Optional[Point] = None,
    ) -> Iterator[Point]:
        point = next(point_sequence, None)
        if not point:
            return sequence_with_no_successive_off_points

        if not last_point_added:
            return self._remove_off_off_sequence_of_points_by_putting_an_on_point_in_between_them(
                point_sequence,
                chain(sequence_with_no_successive_off_points, iter([point])),
                point,
            )
        if point.is_off() and last_point_added.is_off():
            virtual_on_point_in_between = (point + last_point_added) / 2
            return self._remove_off_off_sequence_of_points_by_putting_an_on_point_in_between_them(
                point_sequence,
                chain(
                    sequence_with_no_successive_off_points,
                    iter([virtual_on_point_in_between, point]),
                ),
                point,
            )
        else:
            return self._remove_off_off_sequence_of_points_by_putting_an_on_point_in_between_them(
                point_sequence,
                chain(
                    sequence_with_no_successive_off_points,
                    iter([point]),
                ),
                point,
            )
