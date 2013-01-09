from xml.dom import minidom
import string
import sys

for arg in sys.argv:
	if arg[-3:] == 'xml':
		infile = open(arg)
		idname = arg[:-4].split('/')[-1]
		outfile = open(idname + '.txt', 'w')
		xmlfile = minidom.parse(infile)
		infile.close()
		author = xmlfile.getElementsByTagName('author')[1].toxml()
		letters = xmlfile.getElementsByTagName('div1')
		for letter in letters:
			letternum = letter.attributes['n'].value
			letterid = idname + ',' + letternum
			for node in letter.childNodes:
				if node.nodeName == 'head':
					for headnode in node.childNodes:
						line = unicode(headnode.nodeValue)
						if line[0] == ')':
							lettertitle_list = line.split(' ')[1:]
							lettertitle = ''
							for word in lettertitle_list:
								lettertitle = lettertitle + '_' + word
							lettertitle = lettertitle.lstrip('_')
							if lettertitle == '':
								lettertitle = 'UNKOWN'
						if headnode.nodeName == 'date':
							if headnode.attributes['n'].value != '':
								date = headnode.attributes['n'].value
							else:
								date = 'NONE'
				elif node.nodeName == 'p':
					for textnode in node.childNodes:
						textdata = node.toxml()
						lettertext = ''
						i = 0
						while i < len(textdata):
							if textdata[i] == '<':
								xmlnode = ''
								while textdata[i] != '>':
									xmlnode = xmlnode + textdata[i]
									i = i + 1
								if xmlnode[1:3] == 'pb':
									pagenum = ''
									for char in xmlnode:
										if char.isdigit():
											pagenum = pagenum + char
									lettertext = lettertext + ' <P_' + pagenum + '> '
								i = i + 1
							elif textdata[i] == '\n':
								i = i + 1
							else:
								lettertext = lettertext + textdata[i]
								i = i + 1
			outfile.write(u'ID:' + idname + u',' + letternum + u'\n')
			print u'ID:' + idname + u',' + letternum + u'\n'
			outfile.write(u'METADATA:(METADATA (AUTHOR (NAME ' + author.split(' ')[0].rstrip(',') + u')) (LETTER (DATE ' + date + u') (TITLE ' + lettertitle + u')))\n')
			text = u'TEXT:' + unicode(lettertext) + u'\n'
			s = text.encode('utf-8')
			outfile.write(s)
		outfile.close()
