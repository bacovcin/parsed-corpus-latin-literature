#!/usr/bin/env python
# Always include the settings file as the first argument, 
# with the xmls to be converted as the remaining arguments.
# Default.cnf contains the Latin settings.
#List of values in settings file
#METADATA
#POS
#PERSON
#NUMBER
#TENSE
#VOICE
#GENDER
#CASE
#DEGREE
from xml.dom import minidom
import string
from nltk.tree import *
import sys

def find_attr(word,name):
	try:
		if word[1].node == 'META':
			for attr in word[1]:
				if attr.node == name:
					return attr[0]
		else:
			for i in range(len(word)):
				if word[i].node == 'META':
					for attr in word[i]:
						if attr.node == name:
							return attr[0]
	except:
		for i in range(len(word)):
			try:
				if word[i].node == 'META':
					for attr in word[i]:
						if attr.node == name:
							return attr[0]
			except:
				sys.exit('ERROR in the find_attr function')
	sys.exit('ERROR in the find_attr function: ' + str(word) + ',' + name)

def token_split(tree):
	coord = ['CONJ', '.']
	tokens = []
	toknum = 0
	predicates_found = []
	for word in tree:
		try:
			if 'PRED' in find_attr(word,'RELATION'):
				headid = find_attr(word,'HEAD')
				for word2 in tree:
					try:
						if find_attr(word,'ID') == headid:
							if word2.node in coord:
								predicates_found.append(word)
					except:
						continue
		except:
			if word.node == 'ID':
				allid = word[0]
	newbegin = 0
	for i in range(len(predicates_found)):
		newtoken = Tree('IP-MAT', [Tree('ID', [str(allid + string.lowercase[toknum])])])
		toknum = toknum + 1
		if i == len(predicates_found) - 1:
			for k in range(len(tree) - 2, newbegin - 1, -1):
				newtoken.insert(0, tree[k])
		else:
			headid = find_attr(predicates_found[i + 1],'HEAD')
			searchtype = 'COORDHEAD'
			for k in range(len(tree) - 1):
				if tree[k].node in coord:
					if attr(tree[k],'RELATION') == 'AuxY':
						searchtype = 'AuxY'
			if searchtype == 'COORDHEAD':
				for k in range(len(tree) - 1):
					if tree[k].node in coord:
						if attr(tree[k],'ID') == headid:
							newend = k
			else:
				predid = find_attr(predicates_found[i],'ID')
				for k in range(len(tree) - 1):
					if tree[k].node in coord:
						found = 0
						if attr(tree[k],'ID') == headid:
							newend = k
						elif int(attr(tree[k],'ID')) > int(predid):
							if attr2(tree[k],'HEAD') == headid:
								newend = k
								found = 1
						if found == 1:
							break			
			for k in range(newend - 1, newbegin - 1, -1):
				newtoken.insert(0, tree[k])	
			newbegin = newend
		tokens.append(newtoken)
	if len(predicates_found) == 0:
		tokens.append(tree)
	for token in tokens:
		predid = 0
		predhead = -1
		pred = ''
		for i in range(len(token)):
			try:
				if 'PRED' in find_attr(token[i],'RELATION'):
					predid = find_attr(token[i],'ID')
					predhead = find_attr(token[i],'HEAD')
					for k in token[i][1]:
						if token[i][k].node == 'HEAD':
							token[i][1][k][0] = 0
					pred = token[i]
			except:
				continue
		if predhead != 0:
			for i in range(len(token)):
				if token[i] != pred:
					try:
						if attr(token[i],'ID') == predhead:
							for k in range(len(token[i][1])):
								if token[i][1][k].node == 'HEAD':
									token[i][1][k][0] = predid
								if token[i][1][k].node == 'RELATION':
									if token[i][1][k][0] == 'COORD':
										token[i][1][k][0] = 'AuxX'
						if attr(token[i],'HEAD') == predhead:
							for k in range(len(token[i][1])):
								if token[i][1][k].node == 'HEAD':
									token[i][1][k][0] = predid
					except:
						continue
	return tokens

def parse_sentence(words, tokid, outfile):
	# Upload the settings from the settings file
	settings = open(sys.argv[1])
	for line in settings:
		exec line
	tree = Tree('IP-MAT', [])
	# Go through each word in the tree and create a flat tree with the dependency information:
	# (HEAD, ID, RELATION) incoded under the META node, as well as all the morphological info.
	for i in range(len(words)):
		word = words[i]
		if word.attributes['lemma'].value == 'que1': #This is Latin specific, and should be able to be identified in the settings file.
			ortho = Tree('ORTHO', [str('=' + word.attributes['form'].value)])
		else:
			ortho = Tree('ORTHO', [word.attributes['form'].value])
		meta = Tree('META', [Tree('LEMMA', [word.attributes['lemma'].value])])
		if word.attributes['postag'].value[1] != '-':
			meta.append(Tree('PERSON', [PERSON[word.attributes['postag'].value[1]]]))
		if word.attributes['postag'].value[2] != '-':
			meta.append(Tree('NUMBER', [NUMBER[word.attributes['postag'].value[2]]]))
		if word.attributes['postag'].value[3] != '-':
			meta.append(TENSE[word.attributes['postag'].value[3]][0])
			meta.append(TENSE[word.attributes['postag'].value[3]][1])
		if word.attributes['postag'].value[4] != '-':
			meta.append(Tree('MOOD', [MOOD[word.attributes['postag'].value[4]]]))
		if word.attributes['postag'].value[5] != '-':
			meta.append(Tree('VOICE', [VOICE[word.attributes['postag'].value[5]]]))
		if word.attributes['postag'].value[6] != '-':
			meta.append(Tree('GENDER', [GENDER[word.attributes['postag'].value[6]]]))
		if word.attributes['postag'].value[7] != '-':
			meta.append(Tree('CASE', [CASE[word.attributes['postag'].value[7]]]))
		if word.attributes['postag'].value[8] != '-':
			meta.append(Tree('DEGREE', [DEGREE[word.attributes['postag'].value[8]]]))
		meta.append(Tree('ID', [int(word.attributes['id'].value)]))
		meta.append(Tree('HEAD', [int(word.attributes['head'].value)]))
		meta.append(Tree('RELATION', [word.attributes['relation'].value]))
		#LATIN SPECIFIC
		if word.attributes['lemma'].value == 'sum1': 
			wordtree = Tree('BE', [ortho, meta])
		elif word.attributes['lemma'].value == 'qui1':
			wordtree = Tree('WPRO', [ortho, meta])
		elif word.attributes['postag'].value[4] in ['d', 'u']:
			wordtree = Tree('N', [ortho, meta])
		elif word.attributes['postag'].value[4] in ['g']:
			wordtree = Tree('ADJ', [ortho, meta])
		else:
			wordtree = Tree(POS[word.attributes['postag'].value[0]], [ortho, meta])
		tree.append(wordtree)
	# Perseus relies exclusively on punctuation for thier token breaks.  The following routine
	# runs through the Perseus token, and creates a new token for each predicate, and then checks
	# if the predicate is an imperative and changes the IP tag.
	tree.append(Tree('ID', [tokid]))
	tokens = token_split(tree)
	newtokens = []
	for tree in tokens:
		found = 0
		for word in tree:
			try:
				if word.node != 'ID':
					if 'PRED' in find_attr(word,'RELATION'):
						found = 1
						if find_attr(word,'MOOD') == 'IMPERATIVE':
							tree.node = 'IP-IMP'
			except:
				continue
		if found != 1:
			tree.node = 'FRAG'
		newtokens.append(tree)
	tokens = newtokens
	newtokens = []
	for tree in tokens:
		treeid = tree[-1]
		tree.remove(tree[-1])
		atree = Tree('',[METADATA[treeid[0].split(',')[0]],tree,treeid])
		newtree = atree
		print newtree
		outfile.write(str(newtree))
		outfile.write('\n')
		outfile.write('\n')
	return

for arg in sys.argv[2:]:
	docnames = {'Perseus:text:1999.02.0002':'CaesarCommentarii', 'Perseus:text:1999.02.0010':'CiceroInCatilinam', 'Perseus:text:1999.02.0060':'JeromeVulgata', 'Perseus:text:1999.02.0055':'VergilAeneid', 'Perseus:text:1999.02.0029':'OvidMetamorphoses', 'Perseus:text:2007.01.0001':'PetroniusSatyricon', 'Perseus:text:1999.02.0066':'PropertiusElegies', 'Perseus:text:2008.01.0002':'Sallust:BellumCatilinae'}
	tokid = ''
	if arg[-3:] == 'xml':
		infile = open(arg)
		xmlfile = minidom.parse(infile)
		sentences = xmlfile.getElementsByTagName('sentence') # list containing all the sentences
		for sen in sentences:
			if tokid != docnames[sen.attributes['document_id'].value]:
				tokid = docnames[sen.attributes['document_id'].value]
				try:
					if filename != str(tokid+'.psd'):
						outfile.close()
						outfile = open(str(tokid+'.psd'),'w')
						filename = str(tokid+'.psd')
				except:
					outfile = open(str(tokid+'.psd'),'w')
					filename = str(tokid+'.psd')
				subdoc = sen.attributes['subdoc'].value.split(':')
				for value in subdoc:
					aval = value.split('=')
					if aval[0] != 'text':
						tokid = tokid + ',' + aval[0] + aval[1]
			tokid = tokid + '.' + sen.attributes['id'].value
			words = sen.getElementsByTagName('word')
			parse_sentence(words, tokid, outfile)
