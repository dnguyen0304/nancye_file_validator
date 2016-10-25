# -*- coding: utf-8 -*-

import csv
import os

from nose.tools import assert_false, assert_list_equal, raises

from .. import main

try:
    data_directory = os.environ['FILE_VALIDATOR_DATA_DIRECTORY']
except KeyError:
    message = """
The File Validator could not find the data directory in the shell
environment.

To set the data directory for the current shell session, from the
terminal run
    export FILE_VALIDATOR_DATA_DIRECTORY='/home/foo/bar/'

To set the data directory for the current and all future shell
sessions, from the terminal run
    echo 'export FILE_VALIDATOR_DATA_DIRECTORY='/home/foo/bar/' >> ~/.bashrc
"""
    raise(EnvironmentError(message))


def assert_data_equal(left, right):

    """
    Extends nose.tools.assert_list_equal.

    xlrd does not differentiate between integers and floats; both are
    stored as floats. Floats must be conditionally type casted into
    integer string representations.
    """

    processed_left = _smart_float_coerce(data=left)
    processed_right = _smart_float_coerce(data=right)
    assert_list_equal(processed_left, processed_right)


def _smart_float_coerce(data):

    """
    Returns List.

    Conditionally type cast values into their float representation if
    possible.

    Parameters
    ---------
    data : Iterable
    """

    processed_data = []

    for record in data:
        processed_record = list()
        # This does not support handling empty records.
        for value in record:
            try:
                processed_value = float(value)
            except ValueError:
                processed_value = value
            processed_record.append(processed_value)
        processed_data.append(processed_record)

    return processed_data


@raises(AssertionError)
def test_validation_result_unset():

    validation_results = main.ValidationResults()
    validation_results.validate()


def test_base():

    file_path = data_directory + '/' + 'students.csv'
    is_excel = 'n'
    raw_delimiter = '1'
    if_header = '1'

    validation_results = main.main(file_path=file_path,
                                   is_excel=is_excel,
                                   raw_delimiter=raw_delimiter,
                                   if_header=if_header)

    assert_false(validation_results.is_skewed)


def test_primitive_read_excel():

    _test_primitive_read_excel_helper(left='students.xlsx',
                                      right='students.csv')


def test_primitive_read_excel_skewed():

    _test_primitive_read_excel_helper(left='students-skewed.xlsx',
                                      right='students-skewed.csv')


def _test_primitive_read_excel_helper(left, right):

    """
    Returns None.

    Parameters
    ----------
    left : String
        Left file name or path.
    right : String
        Right file name or path.
    """

    xlsx_file_path = data_directory + '/' + left
    csv_file_path = data_directory + '/' + right
    csv_representation = list()

    with open(csv_file_path, 'r') as file:
        for line in csv.reader(file):
            csv_representation.append([unicode(value) for value in line])

    xlsx_representation = main._primitive_read_excel(
        file_path=xlsx_file_path)

    assert_data_equal(xlsx_representation, csv_representation)

