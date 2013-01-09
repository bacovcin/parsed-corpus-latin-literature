import string

def write_to_file(newfile,new,book):
	punctuation = [',','.','"','?',';']
	new = new.lstrip(' ')
	firsttag = ""
	for word in new.split(' '):
		if word == '':
			continue
		elif word[:4] == 'Aen.':
			firsttag = firsttag + ' ' + word + '_LN'
		elif word[-1] in punctuation:
			firsttag = firsttag + ' ' + word[:-1]
			firsttag = firsttag + ' ' + word[-1] + '_.'
		else:
			firsttag = firsttag + ' ' + word
	firsttag = firsttag.lstrip(' ')
	secondtag = []
	newline = ''
	for word in firsttag.split(' '):
		if word == '._.':
			newline = newline + ' ' + word
			secondtag.append(newline.lstrip(' '))
			newline = ''
		elif word == '?_.':
			newline = newline + ' ' + word
			secondtag.append(newline.lstrip(' '))
			newline = ''
		elif '=' in word:
			newline = newline + ' ' + word.split('=')[0] + ' =' + word.split('=')[1]
		else:
			newline = newline + ' ' + word
	tokennum = 1
	for line in secondtag:
		line = line + ' Aeneid' + str(book) + '.' + str(tokennum) + '_ID\n'
		tokennum = tokennum + 1
		print line
		newfile.write(line)


aen16 = open("./aen1-6.txt")
aen712 = open("./aen7-12.txt")
lines16 = aen16.readlines()
lines712 = aen712.readlines()
lines = lines16[0] + lines712[0]
aen16.close()
aen712.close()
newlines = lines.split('\r')
book = 0
newfile = open(str('aen' + str(book) + '_pos.txt'),'w')
new = ''
for line in newlines:
	if len(line.split(' ')) > 3:
		newline = line.split(' ')[0]
		found = 1
		for i in range(len(line.split(' '))):
			if i == 0:
				continue
			elif found <= 2:
				if line.split(' ')[i] == '':
					continue
				else:
					if found == 1:
						if line.split(' ')[i] != book:
							write_to_file(newfile,new,book)
							book = line.split(' ')[i]
							new = ''
							newfile.close()
							newfile = open(str('aen' + str(book) + '_pos.txt'),'w')
					found = found + 1
					newline = newline + '.' + line.split(' ')[i]
			elif line.split(' ')[i] == '':
					continue
			else:
				newline = newline + ' ' + line.split(' ')[i]
		new = new + ' ' + newline
write_to_file(newfile,new,book)
newfile.close()
