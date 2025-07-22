import os

# IMPORTANT: 
# You must map NUC drive: 
# sudo apt update; sudo apt install cifs-utils
# mkdir /mnt/nuc
# sudo mount -t cifs -o user=web,pass=abs0lute //192.168.1.170/samba/MEDIA /mnt/nuc
# Must run the command "sudo /usr/bin/python /home/web/dev/filetools/RenameSubs.py"
# to work around permissions

real = 1

rootpath = '/mnt/nuc/Series/Will Trent Season 2'

text2find = '.SDH.eng'

text2remove = '.SDH.eng'

for path,dirs,files in os.walk(rootpath):

	for filename in files:
			
		found = filename.find(text2find)
		
		if found > 0:

			newfilename = filename.replace(text2remove,'')

			print ('New filename ' + newfilename)
			
			fileSource = os.path.join(path, filename)
				
			fileDest = os.path.join(path, newfilename)
			
			print ('Rename ' + fileSource + ' To ' + fileDest)
			
			if real:
			
				 os.rename(fileSource, fileDest)
				 