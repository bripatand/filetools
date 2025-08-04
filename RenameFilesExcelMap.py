#!/usr/bin/env python3

import os
from pathlib import Path, PurePath
import glob
import argparse
from openpyxl import load_workbook
import csv

SHEET_NAME = 'Sheet1'
KEY_COLUMN = 'A'
VALUE_COLUMN = 'C'


def main(args):

	sourcefolder = '/mnt/c/Users/pb/Videos/Sport/Kravmaga/KravMagaGlobalEN/NewCurriculum/Checkpoints/Graduate'
	#sourcefolder = args.input_dir


	if not os.path.exists(sourcefolder):
		print(f"Source folder '{sourcefolder}' does not exist.")
		return

	if not os.path.isdir(sourcefolder):
		print(f"Source folder '{sourcefolder}' is not a directory.")
		return

	if not os.path.exists(args.map_file):
		print(f"Map file '{args.map_file}' does not exist.")
		return

	if not args.map_file.endswith('.xlsx'):
		print(f"Map file '{args.map_file}' is not an Excel file.")
		return
	
	map_file = args.map_file

	if args.filter:
		filter = args.filter
	else:
		filter = '*.mp4'

	if args.columns:
		key_col = args.columns[0]
		val_col = args.columns[1]
		print(f"Columns passed in argument key-value:{key_col}-{val_col}")
	else:
		key_col = KEY_COLUMN
		val_col = VALUE_COLUMN
		print(f"Default columns key-value:{key_col}-{val_col}")

	if args.sheet:
		sheet_name = args.sheet
		print(f"Sheet name passed in argument:{sheet_name}")
	else:
		sheet_name = SHEET_NAME
		print(f"Default sheet name:{sheet_name}")
	          
	# Load workbook and sheet
	wb = load_workbook(map_file, data_only=True)
	sheet = wb[sheet_name]

	# Read cells from specified columns
	keys = [cell.value for cell in sheet[key_col]]
	values = [cell.value for cell in sheet[val_col]]

	# Create dictionary, skipping rows with missing key or value
	file_map = {
		k: v for k, v in zip(keys, values)
		if k is not None and v is not None
	}

	print(f"File map:")

	for key, value in file_map.items():
		print(f"{key}: {value}")
      
	globarg = sourcefolder + '/**/' + filter

	files = glob.glob(globarg, recursive = True)
     
	nb_files_renamed = 0

	nb_files_unchanged = 0

	for file in files:
		
		# Pure path objects provide path-handling operations which don’t actually access a filesystem
		filepath = PurePath(file)
		ext = filepath.suffix
		parentpath = filepath.parent
		stem = filepath.stem
		filename = filepath.name
            
		if filename in file_map:

			print(f"File found in map '{filename}'")

			newfilename = file_map[filename]

			if newfilename:
				newfilepath=parentpath.joinpath(newfilename)

			print(f"-----------------------------------------------------------------------------------")
			print(f"Origin '{filepath}'")
			print(f"Rename '{newfilepath}'")

			nb_files_renamed += 1	
			print("Renaming file")
			if(not args.test):
				os.rename(filepath, newfilepath)

			else:
				print("Test mode. Skipping")

		else:
			nb_files_unchanged += 1
			print("File not found in map. Skipping")

	nb_files_total = nb_files_renamed + nb_files_unchanged
	
	print(f"{nb_files_renamed} files renamed out of {nb_files_total}")		

     
if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument("input_dir", help="Location of the input folder")
	parser.add_argument("map_file", help="Location of the csv map file")
	parser.add_argument("-c", "--columns", help="2 columns letters, first one is key, second one is value (default 'AC')")
	parser.add_argument("-s", "--sheet", help="sheet to use in Excel file (default 'sheet1')")
	parser.add_argument("-f", "--filter", help="pattern to filter files (default '*.mp4')")
	parser.add_argument("-t", "--test", action='store_true', help="just testing")
	args = parser.parse_args()

	main(args)