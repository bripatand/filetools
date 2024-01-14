import os
import re
import shutil
from pathlib import Path

# IMPORTANT: 
# You must map NUC drive: 
# sudo apt update; sudo apt install cifs-utils
# mkdir /mnt/nuc
# sudo mount -t cifs -o user=web,pass=abs0lute //NUC/samba/MEDIA /mnt/nuc
# Must run the command "sudo /usr/bin/python3.8 /home/web/dev/filetools/RenameSubs.py"
# to work around permissions

real = 1

rootpath = '/mnt/nuc/Series/Boy Swallows Universe Season 1/Subs'

file2primaryfind = '2_eng,English (SDH).srt'
file2secondaryfind = ''

matchPrimary = re.compile(file2primaryfind)

if file2secondaryfind:
	matchSecondary = re.compile(file2secondaryfind)
else:
	matchSecondary = None

for path,dirs,files in os.walk(rootpath):

	for dir in dirs:
		print('path:' + path)
		print('dir:' + dir)
		
		fileSource = os.path.join(path, dir, file2primaryfind)

		if not os.path.exists(fileSource) and matchSecondary:
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
				#os.rename(fileSource, fileDest)
				shutil.copy(fileSource, fileDest)