import os
import re
from wslpath import wslpath

real = 1

rootpath = wslpath(r"D:\TEMP\1883.S01.1080p.BluRay.x265[eztv.re]")

# must escape ( and ) for regular expression
suffix2find = '1883 \(2021\) - S01E'

# suffix2insert = suffix2find

suffix2insert = '1883 (2021) - S01E'

suffix2replace = '1883.S01E'

digits = '[01][0-9]'

matchAll = re.compile(suffix2find + digits)
matchDigit = re.compile(digits)

for path,dirs,files in os.walk(rootpath):

	for filename in files:

		#print ('File ' + filename)
		
		#f = os.path.join(path,filename)
		
		found = matchAll.match(filename)
		
		name, ext = os.path.splitext(filename)
		
		if found:
	
			pos = len(suffix2insert)

			newfilename = suffix2replace + filename[pos:pos+2] + ext
							
			fileSource = os.path.join(path, filename)
				
			fileDest = os.path.join(path, newfilename)
			
			print ('Rename ' + fileSource + ' To ' + fileDest)
			
			if real:
			
				 os.rename(fileSource, fileDest)
				 
				 	
