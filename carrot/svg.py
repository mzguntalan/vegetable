from typing import Tuple, Callable, Optional

from carrot.vector_graphic import VectorGraphic


class Line(VectorGraphic):
    def __init__(
        self,
        start_point: Tuple[float, float],
        end_point: Tuple[float, float],
        num_points_for_approximation: int,
    ):
        f_x = lambda t: start_point[0] + (end_point[0] - start_point[0]) * t
        f_y = lambda t: start_point[1] + (end_point[1] - start_point[1]) * t
        f = lambda t: (f_x(t), f_y(t))
        super().__init__(
            start_point,
            end_point,
            f_portion_s=f,
            num_points_for_approximation=num_points_for_approximation,
        )

    def __repr__(self):
        return f"Line: {self._start_point} -> {self._end_point}"


class QuadraticCurve(VectorGraphic):
    def __init__(
        self,
        start_point: Tuple[float, float],
        end_point: Tuple[float, float],
        control_point: Tuple[float, float],
        num_points_for_approximation: int,
    ):
        f_x = (
            lambda t: ((1 - t) * (1 - t) * start_point[0])
            + (2 * (1 - t) * (t) * control_point[0])
            + (t * t * end_point[0])
        )
        f_y = (
            lambda t: ((1 - t) * (1 - t) * start_point[1])
            + (2 * (1 - t) * (t) * control_point[1])
            + (t * t * end_point[1])
        )
        f = lambda t: (f_x(t), f_y(t))
        super().__init__(
            start_point,
            end_point,
            f_t=f,
            num_points_for_approximation=num_points_for_approximation,
        )

        self._control_point = control_point

    def __repr__(self):
        return f"QCurve: {self._start_point} --> ({self._control_point}) -> {self._end_point}"
