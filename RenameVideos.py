import os

real = 1

rootpath = '../youtube-dl'

text2find = '.mov'

for path,dirs,files in os.walk(rootpath):

	for filename in files:
			
		found = filename.find(text2find)
		
		if found > 0:

			newfilename = filename[0:found+4].replace('é','e')
			
			fileSource = os.path.join(path, filename)
				
			fileDest = os.path.join(path, newfilename)
			
			print ('Rename ' + fileSource + ' To ' + fileDest)
			
			if real:
			
				 os.rename(fileSource, fileDest)
				 