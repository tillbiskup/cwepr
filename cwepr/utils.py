"""This module contains routines that are rather general and that are employed
in multiple other routines.
"""


def are_values_plausible(array):
    """Check whether the values imported are plausible, i.e.
    not extremely high or low.

    Note: In case of a wrong byteorder the values observed can
    reach 10**300 and higher. The threshold of what is considered
    plausible is, so far, rather arbitrary.

    Parameters
    ------
    array: :class:'numpy.array'
    Array to check the values of.
    """
    for v in array:
        if v > 10 ** 4 or v < 10 ** -10:
            return False
    return True
