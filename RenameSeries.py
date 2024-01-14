import os
import re

real = 1

rootpath = 'N:\MEDIA\Series\The Tunnel Season 3'

suffix2find = 'The.Man.in.the.High.Castle.S02E'

suffix2replace = 'MC.2'

digits = '[01][0-9]'

matchAll = re.compile(suffix2find + digits)
matchDigit = re.compile(digits)

for path,dirs,files in os.walk(rootpath):

	for filename in files:
		
		#f = os.path.join(path,filename)
		
		found = matchAll.match(filename)
		
		name, ext = os.path.splitext(filename)
		
		if found:
	
			pos = len(suffix2find)

			newfilename = suffix2replace + filename[pos:pos+2] + ext
							
			fileSource = os.path.join(path, filename)
				
			fileDest = os.path.join(path, newfilename)
			
			print ('Rename ' + fileSource + ' To ' + fileDest)
			
			if real:
			
				 os.rename(fileSource, fileDest)
				 
				 	
