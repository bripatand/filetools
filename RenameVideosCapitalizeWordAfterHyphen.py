#!/usr/bin/env python3
#Transform "filename KMG_G109_Defenses-headlocks-chokes-ground.mp4" into "KMG_G109_Defenses-Headlocks-Chokes-Ground.mp4"


import os
from pathlib import Path, PurePath
import glob
import argparse
import re

def capitalize_after_hyphen(s):
    return re.sub(r'-(\w)', lambda match: '-' + match.group(1).upper(), s)


def main(args):

	sourcefolder = '/mnt/d/Sports/Fighting/Kravmaga/KravMagaGlobal/KravMagaGlobalEN/KravMagaGlobalUniversity/NewCurriculum/Checkpoints/Graduate'
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
		relativepath = parentpath.relative_to(sourcefolder)

		#print(f"ext {ext}")
		#print(f"parentpath {parentpath}")
		#print(f"stem {stem}")
		#print(f"relative {relativepath}")

		if args.suffix:
			suffix = args.suffix
		else:
			suffix = ''

		modified_stem = capitalize_after_hyphen(stem)

		#print(f"modified stem {modified_stem}")

		# Must use Path and not PurePath to be able to call mkdir method on the object later
		deststem = parentpath.joinpath(modified_stem, suffix)
		
		destpath = str(deststem) + ext

		print(f"-----------------------------------------------------------------------------------")
		print(f"Origin '{stem}'")
		print(f"Rename '{modified_stem}'")

		if stem != modified_stem:
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
	parser.add_argument("-f", "--filter", help="pattern to filter files (default '*.mp4')")
	parser.add_argument("-s", "--suffix", help="Suffix added to output filename")
	parser.add_argument("-t", "--test", action='store_true', help="just testing")
	args = parser.parse_args()

	main(args)