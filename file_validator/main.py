#!/usr/bin/env python
# -*- coding: utf-8 -*-

import StringIO
import csv
import warnings

import pandas as pd
import xlrd
from nose.tools import assert_is_not_none


# Classes
# NOTE (nancye): classes put in other objects that they are similar to - 'inheritance'
# NOTE (nancye): This is how to define a custom exception.
class SkewedDataError(Exception):
    pass


class DataTable(list):

    @classmethod
    def from_delimited(cls, file_path, delimiter):

        """
        Returns DataTable.

        Alternate constructor when converting from text files with
        delimited data.

        Parameters
        ----------
        file_path : String
            File name or path.
        delimiter : String
            Character defining the boundary between record values.
        """

        with open(file_path, 'rb') as file:
            data = [record for record in csv.reader(file, delimiter=delimiter)]
        return DataTable(data)

    @classmethod
    def from_data_frame(cls, data_frame):

        """
        Returns DataTable.

        Alternate constructor when converting from pandas' data frames.

        Parameters
        ----------
        data_frame : pandas.DataFrame
        """

        file = StringIO.StringIO(data_frame.to_csv(index=False))
        data = [record for record in csv.reader(file)]
        return DataTable(data)


class ValidationResults(object):

    def __init__(self,
                 source_data_table=None,
                 processed_data_table=None,
                 is_skewed=None):

        # To track a new validation result:
        #   1. Add it as a new parameter to __init__()'s call signature.
        #   2. Set its default value to None.
        #   3. Set an instance attribute by the same name within
        #      __init__().
        #
        # For example:
        #     # before
        #     def __init__(self):
        #         pass
        #
        #     # after
        #     def __init__(self, is_foo=None):
        #         self.is_foo = is_foo

        self.source_data_table = source_data_table
        self.processed_data_table = processed_data_table
        self.is_skewed = is_skewed

    def validate(self):

        """
        Returns None.

        Assert that all public attributes are not None.

        Raises
        ------
        AssertionError
        """

        message = 'The validation result for "{result}" was not set.'

        results = [attribute
                   for attribute in dir(self)
                   if not attribute.startswith('_') and attribute != 'validate']

        for result in results:
            if result == 'processed_data_table':
                warnings.warn(message.format(result=result))
            else:
                assert_is_not_none(getattr(self, result),
                                   msg=message.format(result=result))


# Functions
def handle_header(header_file_path, delimiter):
    header_data_frame = pd.read_table(header_file_path, sep=delimiter)
    headers = header_data_frame.columns.tolist()

    return headers


def handle_file_path(file_path):
    index = file_path.rfind('.')
    file_path_returned = file_path[:index] + '-with-header' + file_path[index:]

    return file_path_returned


def print_skewness(file, delimiter):
    data = [record for record in csv.reader(file, delimiter=delimiter)]
    for row in data:
        if len(row) != len(data[0]):
            print data[0]
            skewed_line_number = data.index(row) + 1
            one_before = data.index(row) - 1
            one_after = data.index(row) + 1
            print 'The line number of the skewed row is: ', skewed_line_number
            print data[one_before]
            print row
            print data[one_after]


def print_headers(data_frame):
    for column in data_frame:
        print column + ': ' + str(len(data_frame[column].unique()))
        if len(data_frame[column].unique()) <= 20:
            for unique_value in data_frame[column].unique():
                print ' - ' + str(unique_value)
        print ''


# TODO (duyn): Isolate the filesystem I/O to simplify testing.
def is_not_skewed(file_path, delimiter, header_file_path=None):

    """
    Returns Dictionary.

    Determine if the data is skewed.

    "Skewness" describes data where the longest record of the body is
    longer than the header. Empty fields at the tail of the header are
    not included in the count.

    Parameters
    ----------
    file_path : String
        File name or path.
    delimiter : String
        Character defining the boundary between record values.
    header_file_path : String, default None
        File name or path to the header.
    """

    # NOTE (nancye): Sets are similar to lists except sets contain only
    #   unique values. In addition, instead of using .append(), you use
    #   .add().
    line_lengths = dict()
    data = list()
    body_line_lengths = set()

    # NOTE (nancye): open() returns a file object.
    with open(file_path, 'rb') as file:
        # NOTE (nancye): csv.reader() is a function that accepts a
        #   file object and returns an iterable.
        for line in csv.reader(file, delimiter=delimiter):
            data.append(line)
            body_line_lengths.add(len(line))
    line_lengths['body'] = max(body_line_lengths)

    if header_file_path:
        headers = handle_header(header_file_path=header_file_path,
                                delimiter=delimiter)
        line_lengths['header'] = len(headers)
    else:
        line_lengths['header'] = len(data[0])

    return line_lengths['header'] >= line_lengths['body']


def convert_excel_to_csv(file_path):

    """
    Returns String.

    Read an XLS or XLSX file and write it formatted as a CSV.

    The destination file path is qualified with "_processed".

    Parameters
    ----------
    file_path : String
        File name or path.
    """

    new_file_path = file_path.split('.')[0] + '_processed.csv'
    data = _primitive_read_excel(file_path=file_path)

    with open(new_file_path, 'wb') as file:
        csv.writer(file).writerows(data)

    return new_file_path


def _primitive_read_excel(file_path):

    """
    Returns List.

    Read an XLS or XLSX file.

    Parameters
    ----------
    file_path : String
        File name or path.
    """

    data = list()
    worksheet = xlrd.open_workbook(file_path).sheet_by_index(0)

    for row in worksheet.get_rows():
        processed_row = list()
        for cell in row:
            processed_row.append(unicode(cell.value))
        data.append(processed_row)

    return data


def main(file_path='',
         is_excel=None,
         raw_delimiter='',
         has_header=None,
         header_file_path=''):

    validation_results = ValidationResults()

    # Ask for the file path.
    file_path = file_path or raw_input('Please specify the full path to this data file: ')

    # Ask if it is an XLS / XLSX file.
    is_excel = (is_excel
                if is_excel is not None
                else raw_input('Is this an Excel file?  Y / n: ').lower() == 'y')

    if is_excel:
        excel_file_path = convert_excel_to_csv(file_path=file_path)
        # Redefine the existing file_path variable so the Excel file,
        # which has now been converted to CSV, can move through the
        # same validation pipeline.
        file_path = excel_file_path
        real_delimiter = ','

        # Display the first couple of lines so the user can identify
        # the delimiter.
        # TODO (duyn): There will be bonus points for whoever can refactor this duplicated code.
        with open(file_path) as file:
            head = [next(file) for x in xrange(2)]
        print head
    else:
        with open(file_path) as file:
            head = [next(file) for x in xrange(2)]
        print head

        # Ask for the delimiter.
        delimiter_mapping = {
            1: ',',
            2: '\t',
            3: '|',
            4: ';',
            5: ' ',
            6: '-'
        }

        while True:
            raw_delimiter = raw_delimiter or raw_input(
                """According to the printed text, please enter the delimiter used in this file:
                Type 1 for comma (,)
                Type 2 for tab (   )
                Type 3 for pipe character (|)
                Type 4 for semicolon (;)
                Type 5 for space ( )
                Type 6 for hyphen (-)
                """
            )
            try:
                real_delimiter = delimiter_mapping[int(raw_delimiter)]
                break
            except (ValueError, KeyError):
                print 'That is not a valid delimiter. Please try again.'
            except KeyboardInterrupt:
                break

    while True:
        # Ask if a header exists.
        has_header = (has_header
                      if has_header is not None
                      else raw_input('Does this file have a header?  Y / n: ').lower() == 'y')

        try:
            if has_header:
                if is_excel:
                    # Replace the existing header with a processed one.
                    with open(file_path) as file:
                        data = [record for record in csv.reader(file)]
                    header = data[0]

                    processed_header = list()
                    for field in header:
                        if field != '':
                            processed_header.append(field)
                        else:
                            break

                    data[0] = processed_header
                    with open(file_path, 'wb') as file:
                        csv.writer(file).writerows(data)
                if is_not_skewed(file_path=file_path, delimiter=real_delimiter):
                    data_frame = pd.read_table(file_path, sep=real_delimiter)

                    processed_data_table = DataTable.from_data_frame(data_frame)
                    validation_results.processed_data_table = processed_data_table
                    validation_results.is_skewed = False

                    print 'This file is not skewed. Awesome.'
                else:
                    validation_results.is_skewed = True
                    raise SkewedDataError
            else:
                print 'This file does not have a header. Please append one.'
                header_file_path = header_file_path or raw_input(
                    """Please specify the full path to the headers file (It """
                    """must be formatted as a CSV): """)

                # Read in the header.
                with open(header_file_path, 'rb') as file:
                    header = file.read()
                # Read in the body.
                with open(file_path, 'rb') as file:
                    body = file.read()

                # Create a file with the header and body data combined.
                file_path_returned = handle_file_path(file_path)
                with open(file_path_returned, 'wb') as file:
                    file.writelines([header, body])

                if is_not_skewed(file_path=file_path,
                                 delimiter=real_delimiter,
                                 header_file_path=header_file_path):
                    data_frame = pd.read_csv(file_path_returned, sep=real_delimiter)
                    validation_results.is_skewed = False
                    message = ("""The data is not skewed, now has a header, and """
                               """has been returned to you for further testing.""")
                    print message
                else:
                    validation_results.is_skewed = True
                    raise SkewedDataError
            # Display the fields labels along with the corresponding
            # unique field values.
            print_headers(data_frame)
            break
        # Catch the SkewedDataError and display the skewed line along
        # with some context.
        except SkewedDataError:
            print 'Failure. This file is skewed.'
            if has_header:
                with open(file_path, 'rb') as file:
                    print_skewness(file=file, delimiter=real_delimiter)
            else:
                with open(file_path_returned, 'rb') as file:
                    print_skewness(file=file, delimiter=real_delimiter)
            break
        except (KeyError, ValueError):
            print 'That is not a valid response. Please try again.'

        # If it is an XLS or XLSX file, delete the temporary file. Only
        # in cases where the header is appended should the processed
        # file be returned.

    validation_results.validate()

    return validation_results


if __name__ == '__main__':
    main()

