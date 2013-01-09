import string
punctuation = [',','.','"','?',';']
aen1 = open("./aen1.txt")
lines = aen1.readlines()
aen1.close()
new = ""
for line in lines:
	new = new + ' ' + line.rstrip('\n')
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
	else:
		newline = newline + ' ' + word
tokennum = 1
newfile = open('aen1_new.txt','w')
for line in secondtag:
	line = line + ' Aeneid1.' + str(tokennum) + '\n'
	tokennum = tokennum + 1
	newfile.write(line)
newfile.close()
