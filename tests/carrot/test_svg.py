from carrot.svg import Line, QuadraticCurve
from itertools import count, repeat
import operator


def test_line():
    start_point = (0.15, 0.35)
    end_point = (0.61, 0.23)
    line = Line(start_point, end_point, num_points_for_approximation=10)

    for point, reference_point in zip(
        map(lambda x: line(x), [0, 1]), [start_point, end_point]
    ):
        for coordinate, reference_coordinate in zip(point, reference_point):
            assert round(coordinate, 2) == round(reference_coordinate, 2)


def test_degenerate_quadratic_curve():
    start_point = (0.15, 0.35)
    end_point = (0.61, 0.23)
    control_point = (
        0.5 * (start_point[0] + end_point[0]),
        0.5 * (start_point[1] + end_point[1]),
    )

    line = Line(start_point, end_point, num_points_for_approximation=10)
    degenerate_curve = QuadraticCurve(
        start_point, end_point, control_point, num_points_for_approximation=10
    )

    paramters_for_both_vector_graphics = list(
        map(operator.truediv, range(0, 10 + 1), repeat(10))
    )
    points_on_line = map(lambda z: line(z), paramters_for_both_vector_graphics)
    points_on_degenerate_curve = map(
        lambda z: degenerate_curve(z), paramters_for_both_vector_graphics
    )

    for point_on_line, point_on_degenerate_curve in zip(
        points_on_line, points_on_degenerate_curve
    ):
        for coordinate, reference_coordinate in zip(
            point_on_line, point_on_degenerate_curve
        ):
            assert round(coordinate, 2) == round(reference_coordinate, 2)

    assert round(line.get_approximate_length(), 2) == round(
        degenerate_curve.get_approximate_length(), 2
    )


def test_addition():
    start_point = (0.15, 0.35)
    end_point = (0.61, 0.23)
    control_point = (
        0.5 * (start_point[0] + end_point[0]) + 0.5,
        0.5 * (start_point[1] + end_point[1]) + 0.3,
    )

    line = Line(start_point, end_point, num_points_for_approximation=10)
    curve = QuadraticCurve(
        end_point, (0.12, 0.52), control_point, num_points_for_approximation=10
    )

    combination = line + curve

    assert round(combination.get_approximate_length(), 2) == round(
        line.get_approximate_length() + curve.get_approximate_length(), 2
    )
