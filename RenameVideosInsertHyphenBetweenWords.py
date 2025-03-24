#!/usr/bin/env python3
#Transform "filename KMG_G109_DefensesHeadlocksChokesGround.mp4" into "KMG_G109_Defenses-Headlocks-Chokes-Ground.mp4"


import os
from pathlib import Path, PurePath
import glob
import argparse
import re

def capitalize_after_hyphen(s):
    return re.sub(r'-(\w)', lambda match: '-' + match.group(1).upper(), s)


def main(args):

	sourcefolder = '/mnt/d/Sports/Fighting/Kravmaga/KravMagaGlobal/KravMagaGlobalEN/CurriculumBefore2021'
	#sourcefolder = args.input_dir
	
	if args.filter:
		filter = args.filter
	else:
		filter = '*.mp4'

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
		relativepath = parentpath.relative_to(sourcefolder)

		if args.suffix:
			suffix = args.suffix
		else:
			suffix = ''

		print(f"-----------------------------------------------------------------------------------")	
		print(f"Origin '{filename}'")

		# Split the filename into prefix and the part to be modified
		match = re.match(r"(.+?_.+?_)([A-Za-z0-9]+)(\..+)", filename)

		if match:
			prefix, name, extension = match.groups()
 			# Insert hyphens between capitalized words and numbers
			modified_name = re.sub(r'(?<=[a-zA-Z])(?=[A-Z0-9])|(?<=\d)(?=[A-Za-z])', '-', name)

			# Construct the new filename
			new_filename = f"{prefix}{modified_name}{suffix}{extension}"
		else:
			new_filename = f"{filename}{suffix}{ext}"

		# Must use Path and not PurePath to be able to call mkdir method on the object later
		destpath = parentpath.joinpath(new_filename)

		print(f"Rename '{new_filename}'")

		if filename != new_filename:
			nb_files_renamed += 1	
			print("Renaming file")
			if(not args.test):
				os.rename(filepath, destpath)
		else:
			nb_files_unchanged += 1
			print("Skipping file")			
	

	nb_files_total = nb_files_renamed + nb_files_unchanged
	
	print(f"{nb_files_renamed} files renamed out of {nb_files_total}")




if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument("input_dir", help="Location of the input folder")
	parser.add_argument("-p", "--position", help="Position could be a number of second or hh:mm:ss")
	parser.add_argument("-f", "--filter", help="pattern to filter files (default '*.mp4')")
	parser.add_argument("-s", "--suffix", help="Suffix added to output filename")
	parser.add_argument("-t", "--test", action='store_true', help="just testing")
	args = parser.parse_args()

	main(args)