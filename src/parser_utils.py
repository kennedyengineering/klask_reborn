from argparse import ArgumentTypeError
from os import path

# TODO: add ParseLib, filsystem.py and number.py files to organize checks. Add tests. Make package.


def check_positive_int(value):
    """
    Ensure value is g.t. zero integer
    """

    try:
        ivalue = int(value)
    except:
        raise ArgumentTypeError("Expected integer, got %s" % (value))

    if ivalue <= 0:
        raise ArgumentTypeError("Expected positive integer value, got %s" % (value))

    return ivalue


def check_positive_float(value):
    """
    Ensure value is g.t. zero float
    """

    try:
        fvalue = float(value)
    except:
        raise ArgumentTypeError("Expected float, got %s" % (value))

    if fvalue <= 0.0:
        raise ArgumentTypeError("Expected positive float value, got %s" % (value))

    return fvalue


def check_restricted_float(value):
    """
    Ensure value is float in range [0.0, 1.0]
    """

    try:
        fvalue = float(value)
    except:
        raise ArgumentTypeError("Expected float, got %s" % (value))

    if fvalue < 0.0 or fvalue > 1.0:
        raise ArgumentTypeError(
            "Expected float value in range [0.0, 1.0], got %s" % (value)
        )

    return fvalue


def check_directory(value):
    """
    Ensure path is a valid directory
    """

    if not path.isdir(value):
        raise ArgumentTypeError("Expected directory, got %s" % (value))

    return value


def check_file(value):
    """
    Ensure path is a valid file
    """

    if not path.isfile(value):
        raise ArgumentTypeError("Expected file, got %s" % (value))

    return value
