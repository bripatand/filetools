import os
import re
from pathlib import Path

# Must map NUC druve with command: sudo mount -t cifs -o user=web,pass=***** //NUC/samba/MEDIA /mnt/nuc

real = 1

rootpath = '/mnt/nuc/Series/Luther.S01.1080p.BluRay.x265-RARBG'

#rootpath = '/mnt/t/ToBeDeleted'

file2primaryfind = '3_English.srt'
file2secondaryfind = '2_English.srt'

matchPrimary = re.compile(file2primaryfind)
matchSecondary = re.compile(file2secondaryfind)

for path,dirs,files in os.walk(rootpath):

	for dir in dirs:
		#print('path:' + path)
		#print('dir:' + dir)
		
		fileSource = os.path.join(path, dir, file2primaryfind)

		if not os.path.exists(fileSource):
			fileSource = os.path.join(path, dir, file2secondaryfind)

		if os.path.exists(fileSource):
			#print("found file:" + fileSource)

			name, ext = os.path.splitext(fileSource)

			foldername = os.path.basename(os.path.normpath(path))
				
			parent_dir = str(Path(path).parents[0])

			#print ('Parent dir:' + parent_dir)

			fileDest = os.path.join(parent_dir, dir + ext)

			print ('Rename ' + fileSource + ' To ' + fileDest)
				
			if real:
				
				os.rename(fileSource, fileDest)