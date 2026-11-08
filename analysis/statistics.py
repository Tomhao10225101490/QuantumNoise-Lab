from math import sqrt


def wilson(errors, shots, z=1.959963984540054):
    if shots <= 0 or not 0 <= errors <= shots:
        raise ValueError("Invalid binomial counts")
    r = errors / shots
    center = (r + z * z / (2 * shots)) / (1 + z * z / shots)
    half = (
        z
        * sqrt(r * (1 - r) / shots + z * z / (4 * shots * shots))
        / (1 + z * z / shots)
    )
    # Clamp round-off at endpoints so plotted interval lengths stay nonnegative.
    return max(0, min(r, center - half)), min(1, max(r, center + half))
