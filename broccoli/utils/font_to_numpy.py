from broccoli.font import Font
import numpy as np


def scale_font_array_to_negative_1_to_positive_1(
    font_as_array: np.ndarray,
) -> np.ndarray:
    x_values = font_as_array[:, :, 0]
    y_values = font_as_array[:, :, 1]

    max_x_values = np.max(x_values, axis=-1)
    max_y_values = np.max(y_values, axis=-1)

    min_x_values = np.min(x_values, axis=-1)
    min_y_values = np.min(y_values, axis=-1)

    trans_x = -(min_x_values + max_x_values) / 2.0
    trans_y = -(min_y_values + max_y_values) / 2.0

    scale_x = abs(max_x_values + trans_x)
    scale_y = abs(max_y_values + trans_y)

    scale = np.max(np.stack([scale_x, scale_y], axis=1), axis=-1)
    translation = np.stack([trans_x, trans_y], axis=-1)

    font_as_array = font_as_array + np.expand_dims(translation, axis=1)
    font_as_array = font_as_array / np.expand_dims(
        np.expand_dims(scale, axis=-1), axis=-1
    )
    return font_as_array


def font_to_numpy(font: Font, scaled: bool = True) -> np.ndarray:
    glyphs = []
    for glyph_name in font:
        glyph = font(glyph_name)
        glyphs.append(list(glyph.get_as_point_sequence()))
    font_as_array = np.array(glyphs)

    if scaled:
        font_as_array = scale_font_array_to_negative_1_to_positive_1(font_as_array)

    return font_as_array
