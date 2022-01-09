import os
import argparse
import pathlib


def check_input_dir(value):
    """
    Check input directory exists.
    """
    if not os.path.isdir(value):
        raise argparse.ArgumentTypeError('Directory provided is not valid!')
    return value


def check_input_path(value):
    """
    Check input file exists.
    """
    if not os.path.exists(value):
        raise argparse.ArgumentTypeError('Input file does not appear to exist.')
    return value


def check_output_dir(value):
    """
    Check output directory does not contain illegal characters, and create the directory if
    it doesn't exist.
    """
    try:
        output_path = pathlib.Path(value)
        output_path.mkdir(parents=True, exist_ok=True)
        return value
    except OSError:
        raise argparse.ArgumentTypeError('Output directory is not a valid path.')


def check_output_path(value):
    """
    Check if path is valid, create directories if necessary.
    """
    try:
        output_path = pathlib.Path(value)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        return value
    except OSError:
        raise argparse.ArgumentTypeError('Output path is not a valid path.')


def check_positive(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError(f'{value} must be positive integer.')
    return ivalue
