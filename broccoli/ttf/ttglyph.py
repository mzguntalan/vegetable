from typing import Iterable, List, Optional, Tuple
from itertools import chain
from unittest.mock import sentinel


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


class Contour:
    def __init__(self, point_sequence: Iterable[Point]):
        self._point_sequence = self._decompress(point_sequence)

    @property
    def point_sequence(self):
        return self._point_sequence

    def _decompress(self, point_sequence: Iterable[Point]) -> Iterable[Point]:
        return self._remove_off_off_sequence_of_points_by_putting_an_on_point_in_between_them(
            self._fix_end_points(point_sequence)
        )

    def _fix_end_points(self, point_sequence: Iterable[Point]) -> List[Point]:
        point_sequence = list(point_sequence)
        first_point, last_point = point_sequence[0], point_sequence[-1]

        copy_last_point_to_the_beginning_of_sequence = (
            lambda sequence: [sequence[-1]] + sequence
        )
        put_point_in_beginning_and_last_of_sequence = (
            lambda point, sequence: [point] + sequence + [point]
        )

        if first_point.is_off():
            if last_point.is_on():
                point_sequence = copy_last_point_to_the_beginning_of_sequence(
                    point_sequence
                )
            else:
                virtual_point_in_between = (first_point + last_point) / 2
                point_sequence = put_point_in_beginning_and_last_of_sequence(
                    point=virtual_point_in_between, sequence=point_sequence
                )

        first_point, last_point = point_sequence[0], point_sequence[-1]
        if last_point != first_point:
            point_sequence.append(first_point)

        return point_sequence

    def _remove_off_off_sequence_of_points_by_putting_an_on_point_in_between_them(
        self,
        point_sequence: Iterable[Point],
        point_sequence_with_no_successive_off_points: Iterable[Point] = (),
        last_point_added_to_no_successive_off_points: Optional[Point] = None,
    ) -> Iterable[Point]:
        point_sequence = iter(point_sequence)
        incoming_point = next(point_sequence, None)
        if incoming_point is None:
            return point_sequence_with_no_successive_off_points

        if last_point_added_to_no_successive_off_points is None:
            return self._remove_off_off_sequence_of_points_by_putting_an_on_point_in_between_them(
                point_sequence,
                point_sequence_with_no_successive_off_points=chain(
                    point_sequence_with_no_successive_off_points, iter([incoming_point])
                ),
                last_point_added_to_no_successive_off_points=incoming_point,
            )

        virtual_on_point_in_between = (
            incoming_point + last_point_added_to_no_successive_off_points
        ) / 2

        return self._remove_off_off_sequence_of_points_by_putting_an_on_point_in_between_them(
            point_sequence,
            point_sequence_with_no_successive_off_points=chain(
                point_sequence_with_no_successive_off_points,
                iter([virtual_on_point_in_between, incoming_point]),
            ),
            last_point_added_to_no_successive_off_points=incoming_point,
        )
