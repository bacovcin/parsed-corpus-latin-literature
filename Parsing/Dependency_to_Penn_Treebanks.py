# The input files need to be flat trees containing only the terminal
# nodes and all three pieces of dependency information (ID, HEAD, 
# RELATION) in thier META nodes.
from xml.dom import minidom
import string
from nltk.tree import *
import sys

def find_label(fword, headword, objects, phrase):
	modifiers = ['ADJP', 'IP-PPL', 'ADVP', 'NUMP']
	verbs = ['VB', 'BE']
	nominals = ['N', 'PRO', 'WPRO']
	frel = find_attr(fword,'RELATION')
	print frel
	if 'SBJ' in frel:
		if fword.node in nominals:
			newlabel = 'NP-SBJ'
		elif fword.node in verbs:
			if find_attr(fword,'MOOD') == 'INFINITIVE':
				newlabel = 'IP-INF-SBJ'
			else:
				if phrase.node == 'CP':
					newlabel = 'IP-SUB'
					phrase.node = 'CP-THT'
				else:
					newlabel = 'CP-FRL-SBJ'
		else:
			newlabel = 'XP-XXX'
	elif 'OBJ' in frel:
		if fword.node in nominals:
			if headword.node == 'VB':
				if objects == 0:
					newlabel = 'NP-OB1'
					objects = objects + 1
				else:
					newlabel = 'NP-OBX'
					objects = objects + 1
			elif headword.node == 'P':
				newlabel = 'NP'
			else:
				newlabel = 'NP-OBX'
		elif fword.node in verbs:
			if find_attr(fword,'MOOD') == 'INFINITIVE':
				newlabel = 'IP-INF'
			else:
				if phrase.node == 'CP':
					newlabel = 'IP-SUB'
					phrase.node = 'CP-THT'
					objects = objects + 1
				else:
					newlabel = 'CP-FRL-OB1'
					objects = objects + 1
		else:
			newlabel = fword.node + 'P'
	elif ('ATR' in frel) or ('ATV' in frel):
		if fword.node == 'ADJ':
			newlabel = 'ADJP'
		elif fword.node == 'VB-ADJ':
			newlabel = 'IP-PPL'
		elif fword.node == 'NUM':
			newlabel = 'NUMP'
		elif fword.node in verbs:
			newlabel = 'CP-REL'
		elif fword.node in nominals:
			if headword.node == 'P':
				newlabel = 'NP'
			else:
				fcase = find_attr(fword,'CASE')
				if find_attr(headword,'CASE') == fcase:
					newlabel = 'NP-PRN'
				else:
					if fcase == 'GENITIVE':
						newlabel = 'NP-POS'
					else:
						newlabel = 'NP-XXX'
		else:
			newlabel = 'XP-XXX'
	elif ('ADV' in frel) or ('AtvV' in frel):	
		if fword.node == 'ADV':
			newlabel = 'ADVP'
		elif (fword.node in nominals) or (fword.node in ['ADJ','NUM']):
			if headword.node == 'P':
				newlabel = 'NP'
			else:
				newlabel = 'NP-ADV'
		elif fword.node == 'VB-ADJ':
			newlabel = 'IP-PPL-SBJ'
		elif fword.node in verbs:
			if phrase.node == 'CP':
				newlabel = 'IP-SUB'
				phrase.node = 'CP-ADV'
			else:
				newlabel = 'CP-FRL-NP'
	elif 'PNOM' in frel:
		newlabel = 'NP-PRD'
	elif 'OCOMP' in frel:
		newlabel = 'NP-SPR'
	elif 'COORD' in frel:
		newlabel = 'CONJP'
	elif 'APOS' in frel:
		if headword.node in nominals:
			newlabel = 'NP-PRN'
		else:
			newlabel = find_label(headword,headword,objects,phrase)
	elif 'AuxP' in frel:
		newlabel = 'PP'
	elif 'AuxC' in frel:
		fword.node = 'C'
		newlabel = 'CP'
	elif 'AuxR' in frel:
		newlabel = 'NP-OBJ'
	elif 'AuxV' in frel:
		newlabel = 'NONE'
	elif 'AuxX' in frel:
		newlabel = 'NONE'
	elif 'AuxG' in frel:
		newlabel = 'NONE'
		fword.node = '\''
	elif 'AuxK' in frel:
		newlabel = 'NONE'
	elif 'AuxY' in frel:
		if phrase.node == 'CONJP':
			newlabel = 'NONE'
		else:
			newlabel = 'ADVP'
	elif 'AuxZ' in frel:
		newlabel = 'NONE'
		if find_attr(fword,'LEMMA') == 'non1':
			fword.node = 'NEGP'
		else:
			fword.node = 'FP'
	elif 'PRED' in frel:
		newlabel = 'NONE'
	else:
		raw_input(frel)
	return newlabel

