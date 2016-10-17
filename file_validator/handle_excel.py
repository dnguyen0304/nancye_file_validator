import pandas as pd
import xlrd
import os.path
import csv


def is_excel_skewed(file_path):
    book = xlrd.open_workbook(file_path)
    sheet = book.sheet_by_index(0)
    header = sheet.row(0)
    	for cell in header:
		print cell.ctype
		if xlrd.sheet.ctype_text[cell.ctype] == 'empty':
			return True
	return False


def handle_excel(file_path):

	new_file_path = file_path.split('.')[0] + '_processed.csv'				    
        workbook = xlrd.open_workbook(file_path)
	worksheet = workbook.sheet_by_index(0)
	# convert list of cells to list of strings
									    
									        	empty_body = []	
	for source_row in worksheet.get_rows():
		processed_row = [cell.value for cell in source_row]  
		# lambda expression
		empty_body.append(processed_row)
		processed_row = []

										        with open(new_file_path, 'wb') as file:
		writer = csv.writer(file)						        writer.writerows(empty_body)
	return new_file_path
	
file_path=r"C:\Workspace\ma-somerville\test scores\ACCESS 16 Somerville.xlsx"   handle_excel(file_path)
