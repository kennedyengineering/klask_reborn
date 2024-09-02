from argparse import ArgumentTypeError
from os import path


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
