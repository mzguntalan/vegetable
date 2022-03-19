from functools import reduce
from itertools import tee, count, repeat
from typing import Tuple, Optional, Callable, Iterator
import operator


class VectorGraphic:
    def __init__(
        self,
        start_point: Tuple[float, float],
        end_point: Tuple[float, float],
        f_t: Optional[Callable[[float], Tuple[float, float]]] = None,
        f_portion_s: Optional[Callable[[float], Tuple[float, float]]] = None,
        num_points_for_approximation: Optional[int] = 10,
        approximate_length: Optional[float] = None,
    ):
        self._start_point = start_point
        self._end_point = end_point

        if f_t is None and f_portion_s is None:
            raise ValueError("Must pass either f_t or f_portion_s")

        if f_portion_s is not None:
            self._f_portion_s = f_portion_s
        elif f_t is not None:
            self._f_portion_s = self._make_f_portion_s_from_f_t(f_t)

        self._num_points_for_approximation = num_points_for_approximation
        if approximate_length is not None:
            self._approximate_length = approximate_length
        else:
            self._approximate_length = self._get_approximate_length()

    @property
    def num_points_for_approximation(self) -> int:
        return self._num_points_for_approximation

    @num_points_for_approximation.setter
    def num_points_for_approximation(self, input):
        self._num_points_for_approximation = input

    def __call__(self, portion_of_arc_length: float) -> Tuple[float, float]:
        return self._f_portion_s(portion_of_arc_length)

    def _make_f_s_from_f_t(
        self, f_t: Callable[[float], Tuple[float, float]]
    ) -> Callable[[float], Tuple[float, float]]:
        return lambda s: f_t(self._get_t_by_arc_length(f_t, s))

    def _make_f_portion_s_from_f_t(
        self, f_t: Callable[[float], Tuple[float, float]]
    ) -> Callable[[float], Tuple[float, float]]:
        return lambda portion_s: self._make_f_s_from_f_t(f_t)(
            portion_s * self._get_approximate_length_between(f_t, 0, 1)
        )

    def _get_t_by_arc_length(
        self,
        f: Callable[[float], Tuple[float, float]],
        arc_length: float,
        tolerance_decimal_place: Optional[int] = 3,
        max_depth_search: Optional[int] = 20,
    ) -> float:
        arc_length_rounded = round(arc_length, tolerance_decimal_place)

        def _binary_search(start_t: float = 0, end_t: float = 1, num_runs=0):
            t = (start_t + end_t) / 2
            s = self._get_arc_length_from_beginning(f, t)
            s_rounded = round(s, tolerance_decimal_place)
            if s_rounded == arc_length_rounded or num_runs >= max_depth_search:
                return t

            if arc_length_rounded > s_rounded:
                return _binary_search(start_t=t, end_t=end_t, num_runs=num_runs + 1)
            return _binary_search(start_t=start_t, end_t=t, num_runs=num_runs + 1)

        return _binary_search()

    def _get_as_point_sequence_between(
        self,
        f: Callable,
        z_0: float,
        z_1: float,
        num_points_for_approximation: Optional[int] = None,
        include_last_point: Optional[bool] = False,
    ) -> Iterator[Tuple[float, float]]:
        num_points_for_approximation = (
            num_points_for_approximation or self._num_points_for_approximation
        )
        constant_numerator = z_1 - z_0
        constant_denominator = {
            True: num_points_for_approximation - 1,
            False: num_points_for_approximation,
        }

        constant = constant_numerator / constant_denominator[include_last_point]

        nth_point = lambda n: f(constant * n)

        points = map(
            lambda z: nth_point(z),
            range(0, num_points_for_approximation),
        )

        return points

    def get_as_point_sequence(
        self,
        num_points_for_approximation: Optional[int] = None,
        include_last_point: Optional[bool] = False,
    ) -> Iterator[Tuple[float, float]]:
        return self._get_as_point_sequence_between(
            lambda x: self(x),
            0,
            1,
            num_points_for_approximation,
            include_last_point,
        )

    def _get_distance_between_points(
        self, point_0: Tuple[float, float], point_1: Tuple[float, float]
    ) -> float:
        differences_between_coordinates = map(
            lambda coord_0, coord_1: (coord_0 - coord_1) ** 2.0, point_0, point_1
        )
        distance = (sum(differences_between_coordinates)) ** 0.5
        return distance

    def _get_approximate_length_between(
        self,
        f: Callable[[float], Tuple[float, float]],
        z_0: float,
        z_1: float,
        num_points_for_approximation: Optional[int] = None,
    ) -> float:
        points, adjacent_points = tee(
            self._get_as_point_sequence_between(
                f,
                z_0,
                z_1,
                num_points_for_approximation,
                include_last_point=True,
            )
        )
        next(adjacent_points)
        distances_between_adjacent_points = map(
            lambda p_0, p_1: self._get_distance_between_points(p_0, p_1),
            points,
            adjacent_points,
        )
        length = sum(distances_between_adjacent_points)
        return length

    def _get_arc_length_from_beginning(
        self, f: Callable[[float], Tuple[float, float]], z: float
    ) -> float:
        return self._get_approximate_length_between(f, 0, z)

    def _get_approximate_length(
        self, num_points_for_approximation: Optional[int] = None
    ) -> float:
        return self._get_approximate_length_between(
            self._f_portion_s, 0, 1, num_points_for_approximation
        )

    def get_approximate_length(
        self, num_points_for_approximation: Optional[int] = None
    ) -> float:
        if num_points_for_approximation is None:
            return self._approximate_length
        return self._get_approximate_length_between(
            self._f_portion_s, 0, 1, num_points_for_approximation
        )

    def __add__(self, other: "VectorGraphic") -> "VectorGraphic":
        lengths = list(map(lambda vg: vg.get_approximate_length(), [self, other]))
        total_length = sum(lengths)
        normalized_lengths = list(map(operator.truediv, lengths, repeat(total_length)))

        combined_vg_f_portion_of_s = (
            lambda t: self._f_portion_s(t / normalized_lengths[0])
            if 0 <= t <= normalized_lengths[0]
            else other._f_portion_s((t - normalized_lengths[0]) / normalized_lengths[1])
        )

        sum_vg = VectorGraphic(
            start_point=self._start_point,
            end_point=other._end_point,
            f_portion_s=combined_vg_f_portion_of_s,
            num_points_for_approximation=self._num_points_for_approximation
            + other._num_points_for_approximation,
            approximate_length=self.get_approximate_length()
            + other.get_approximate_length(),
        )

        return sum_vg

    def __repr__(self):
        return f"VectorGraphic: {self._start_point} -> {self._end_point}"
