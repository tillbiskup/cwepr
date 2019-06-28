"""Routines that are rather general."""


def are_intensity_values_plausible(array):
    """Check imported values for plausibility.

    Check whether the values imported are plausible, i.e. not extremely high or
    low.

    .. note::
        In case of a wrong byteorder the values observed can reach 10**300
        and higher. The threshold of what is considered plausible is, so far,
        rather arbitrary.

    Parameters
    ----------
    array: :class:`numpy.array`
        Array to check the values of.

    """
    for value in array:
        if value > 10 ** 4 or value < 10 ** -10:
            return False
    return True
