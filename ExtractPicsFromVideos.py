#!/usr/bin/env python3

import os
from pathlib import Path, PurePath
import glob
import argparse


def main(args):

	sourcefolder = '/mnt/d/Sports/Fighting/Kravmaga/KravMagaGlobal/KravMagaGlobalEN/KravMagaGlobalUniversity/NewCurriculum/Checkpoints'
	#sourcefolder = args.input_dir
	
	if args.filter:
		filter = args.filter
	else:
		filter = '*.mp4'

	if args.position:
		position = args.position
	else:
		position = '0'

	globarg = sourcefolder + '/**/' + filter

	if args.out_folder:
		destinationfolder = args.out_folder
	else:
		destinationfolder = sourcefolder

	files = glob.glob(globarg, recursive = True)

	for file in files:
			
		# Pure path objects provide path-handling operations which don’t actually access a filesystem
		filepath = PurePath(file)
		ext = filepath.suffix
		parentpath = filepath.parent
		stem = filepath.stem
		relativepath = parentpath.relative_to(sourcefolder)

		if args.suffix:
			suffix = args.suffix
		else:
			suffix = ''

		# Must use Path and not PurePath to be able to call mkdir method on the object later
		destfolder = Path(destinationfolder).joinpath(relativepath)
		deststem = destfolder.joinpath(stem, suffix)
		destpath = str(deststem) + '.jpg'
		
		print(f"ext {ext}")
		print(f"parentpath {parentpath}")
		print(f"stem {stem}")
		print(f"relative {relativepath}")
		print(f"destfolder {destfolder}")
		print(f"destpath {destpath}")
		print(f"position {position}")

		# Use single quote and double quote inside as some path/filename can contain single quote
		command = f'ffmpeg -i "{file}" -ss {position} -vframes 1  "{destpath}"'
		print('Command:' + command)

		if(not args.test):
			destfolder.mkdir(parents=True, exist_ok=True)

			os.system(command)
			
if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument("input_dir", help="Location of the input folder")
	parser.add_argument("-p", "--position", help="Position could be a number of second or hh:mm:ss")
	parser.add_argument("-o", "--out-folder", help="Output folder. Default is same as input")
	parser.add_argument("-f", "--filter", help="pattern to filter files (default '*.mp4')")
	parser.add_argument("-s", "--suffix", help="Suffix added to output filename")
	parser.add_argument("-t", "--test", action='store_true', help="just testing")
	args = parser.parse_args()

	main(args)