import csv

import xlrd


def is_excel_skewed(file_path):
    book = xlrd.open_workbook(file_path)
    sheet = book.sheet_by_index(0)
    header = sheet.row(0)
    for cell in header:
        print cell.ctype
        if xlrd.sheet.ctype_text[cell.ctype] == 'empty':
            return True
    return False


def convert_excel_to_csv(file_path):

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

    data = []
    worksheet = xlrd.open_workbook(file_path).sheet_by_index(0)

    for row in worksheet.get_rows():
        processed_row = list()
        for cell in row:
            if not xlrd.sheet.ctype_text[cell.ctype] == 'empty':
                processed_row.append(unicode(cell.value))
                continue
        data.append(processed_row)

    return data


if __name__ == '__main__':
    file_path = ''
    convert_excel_to_csv(file_path)

