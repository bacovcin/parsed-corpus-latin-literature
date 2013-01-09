import sys
import os
import string
POSSIBLE_POS_ROOTS = []
POSSIBLE_POS_IRREG = []

class Word():
	ORTHO = ''
	POS = ''

class SuffixC():
	FORM = ""
	POS = ""

class TierSearchOutput():
	Tier0 = SuffixC()

class RootC():
	POS = ""
	
class IrrC():
	FORM = ""
	LEMMA = ""
	POS = ""


def parse_suffix(suffixes):
	myoutput = []
	for line in suffixes:
		if line != '':
			asuf = SuffixC()
			forms = line.rstrip().split(' ')
			asuf.FORM = forms[0]
			for att in forms:
				if str(att) == str(asuf.FORM):
					continue
				else:
					asuf.__dict__[att.split(':')[0]] = att.split(':')[1]
			myoutput.append(asuf)
	return myoutput


def parse_root(roots):
	global POSSIBLE_POS_ROOTS
	myoutput = {}
	endofparameters = 0
	for line in roots:
		if endofparameters == 0:
			if line.rstrip() == '###':
				endofparameters = 1
			else:
				newpos = {}
				for aset in line.split(' '):
					newpos[aset.split(':')[0]] = aset.split(':')[1].rstrip()
				POSSIBLE_POS_ROOTS.append([newpos['POS']])
				for att in newpos.keys():
					if att != 'POS':
						if len(POSSIBLE_POS_ROOTS[-1]) == 1:
							POSSIBLE_POS_ROOTS[-1].append([[att,newpos[att].split('|')]])
						else:
							POSSIBLE_POS_ROOTS[-1][1].append([att,newpos[att].split('|')])
		else:
			if line != '':
				aroot = RootC()
				forms = line.rstrip().split(' ')
				myoutput[forms[0].rstrip()] = aroot
				for att in forms:
					if att in myoutput.keys():
						continue
					else:
						myoutput[forms[0].rstrip()].__dict__[att.split(':')[0]] = att.split(':')[1]
	return myoutput


def parse_irregular(irreg):
	global POSSIBLE_POS_IRREG
	myoutput = []
	endofparameters = 0
	for line in irreg:
		if endofparameters == 0:
			if line.rstrip() == '###':
				endofparameters = 1
			else:
				newpos = {}
				for aset in line.split(' '):
					newpos[aset.split(':')[0]] = aset.split(':')[1].rstrip()
				POSSIBLE_POS_IRREG.append([newpos['POS']])
				if len(newpos.keys()) == 1:
					POSSIBLE_POS_IRREG[-1].append('UNINFLECTED')
				else:
					for att in newpos.keys():
						if att != 'POS':
							if len(POSSIBLE_POS_IRREG[-1]) == 1:
								POSSIBLE_POS_IRREG[-1].append([[att,newpos[att].split('|')]])
							else:
								POSSIBLE_POS_IRREG[-1][1].append([att,newpos[att].split('|')])
		else:
			if line != '':
				airr = IrrC()
				forms = line.rstrip().split(' ')
				airr.FORM = forms[0]
				airr.LEMMA = forms[1]
				for att in forms:
					if att == airr.FORM:
						continue
					elif att == airr.LEMMA:
						continue
					else:
						airr.__dict__[att.split(':')[0]] = att.split(':')[1]
				myoutput.append(airr)
	return myoutput	

def sentence(words):
	output = ''
	for word in words:
		if '_' in word:
			continue
		else:
			output = output + ' ' + str(word)
	output = output.lstrip()
	return(output)
	
def object_out(suf):
	output = ''
	for atr in suf.__dict__.keys():
		try:
			output = output + ' ' + str(atr) +': ' + object_out(suf.__dict__[atr])
		except:
			if atr == 'GENDER':
				if suf.__dict__[atr] not in output:
					output = output + ' ' + suf.__dict__[atr]
			elif atr == 'NUMBER':
				if suf.__dict__[atr] not in output:
					output = output + ' ' + suf.__dict__[atr]
			elif atr == 'CASE':
				if suf.__dict__[atr] not in output:
					output = output + ' ' + suf.__dict__[atr]
			elif atr == 'DEGREE':
				if suf.__dict__[atr] not in output:
					output = output + ' ' + suf.__dict__[atr]
			elif atr == 'TENSE':
				if suf.__dict__[atr] not in output:
					output = output + ' ' + suf.__dict__[atr]
			elif atr == 'MOOD':
				if suf.__dict__[atr] not in output:
					output = output + ' ' + suf.__dict__[atr]
			elif atr == 'ASPECT':
				if suf.__dict__[atr] not in output:
					output = output + ' ' + suf.__dict__[atr]
			elif atr == 'VOICE-MORPH':
				if suf.__dict__[atr] not in output:
					output = output + ' ' + suf.__dict__[atr]
			elif atr == 'VOICE-SEMANTIC':
				if suf.__dict__[atr] not in output:
					output = output + ' ' + suf.__dict__[atr]
			elif atr == 'PERSON':
				if suf.__dict__[atr] not in output:
					output = output + ' ' + suf.__dict__[atr]
			elif atr == 'PERSON-AGR':
				if suf.__dict__[atr] not in output:
					output = output + ' ' + suf.__dict__[atr]
			elif atr == 'NUMBER-AGR':
				if suf.__dict__[atr] not in output:
					output = output + ' ' + suf.__dict__[atr]
			elif atr == 'POS':
				for atr2 in suf.__dict__.keys():
					if atr2 == 'TIER':
						if suf.__dict__[atr2] == '1':
							output = output + ' ' + suf.__dict__[atr]
					elif atr2 == 'FORM':
						output = output + ' ' + suf.__dict__[atr]
	outlist = output.split(' ')
	newout = ''
	for item in outlist:
		if item not in newout:
			newout = newout + ' ' + item
	newout = newout.lstrip()
	return newout
	
def tiersearch(stem, maxtiernum, currenttiernum, suffix, roots):
	currenttier = []
	output = []
	for suf in suffix:
		if suf.TIER == str(currenttiernum):
			currenttier.append(suf)
	for i in range(len(stem)):
		if i == 0:
			for suf in currenttier:
				if suf.FORM == 'NULL':
					if currenttiernum == maxtiernum: 
						if stem in roots.keys():
							same = 0
							for att in roots[stem].__dict__.keys():
								try:
									if suf.__dict__[att] != roots[stem].__dict__[att]:
										if att == 'POS':
											print suf.__dict__[att] + ':' + roots[stem].__dict__[att]
											try:
												if suf.__dict__['PREVIOUS_POS'] != roots[stem].__dict__['POS']:
													same = same + 1
											except:
												same = same + 1
										elif currenttiernum == 1:
											same = same + 1
										else:
											if att != 'DECLENSION':
												same = same + 1
								except:
									continue
							if same == 0:
								newout = TierSearchOutput()
								newout.__dict__['Tier'+str(currenttiernum)] = suf
								newout.STEM = stem
								output.append(newout)
					else:
						options = tiersearch(stem, maxtiernum, int(currenttiernum + 1), suffix, roots)
						if options != []:
							for opt in options:
								same = 0
								for att in opt.__dict__['Tier'+str(currenttiernum + 1)].__dict__.keys():
									if att == 'FORM':
										continue
									elif att == 'TIER':
										continue
									try:
										if suf.__dict__[att] != opt.__dict__['Tier'+str(currenttiernum + 1)].__dict__[att]:
											if att == 'POS':
												try:
													if suf.__dict__['PREVIOUS_POS'] != opt.__dict__['Tier'+str(currenttiernum + 1)].__dict__[att]:
														same = same + 1
												except:
													same = same + 1
											elif currenttiernum == 1:
												same = same + 1
											else:
												if att != 'DECLENSION':
													same = same + 1
									except:
										continue
								if same == 0:
									opt.__dict__['Tier'+str(currenttiernum)] = suf
									output.append(opt)
		else:
			for suf in currenttier:
				if suf.FORM == stem[-i:]:
					if currenttiernum == maxtiernum: 
						if stem[:-i] in roots.keys():
							same = 0
							for att in roots[stem[:-i]].__dict__.keys():
								try:	
									if suf.__dict__[att] != roots[stem[:-i]].__dict__[att]:
										if att == 'POS':
											try:
												if suf.__dict__['PREIVOUS_POS'] != roots[stem[:-i]].__dict__['POS']:
													same = same + 1
											except:
												same = same + 1
										elif currenttiernum == 1:
											same = same + 1
										else:
											if att != 'DECLENSION':
												same = same + 1
								except:
									continue
							if same == 0:
								newout = TierSearchOutput()
								newout.__dict__['Tier'+str(currenttiernum)] = suf
								newout.STEM = stem[:-i]
								output.append(newout)
					else:
						options = tiersearch(stem[:-i], maxtiernum, int(currenttiernum + 1), suffix, roots)
						if options != []:
							for opt in options:
								same = 0
								for att in opt.__dict__['Tier'+str(currenttiernum + 1)].__dict__.keys():
									if att == 'FORM':
										continue
									elif att == 'TIER':
										continue
									try:
										if suf.__dict__[att] != opt.__dict__['Tier'+str(currenttiernum + 1)].__dict__[att]:	
											if att == 'POS':
												try:
													if suf.__dict__['PREVIOUS_POS'] != opt.__dict__['Tier'+str(currenttiernum + 1)].__dict__[att]:
														same = same + 1
												except:
													same = same + 1
											elif currenttiernum == 1:
												same = same + 1
											else:
												if att != 'DECLENSION':
													same = same + 1
									except:
										continue
								if same == 0:
									opt.__dict__['Tier'+str(currenttiernum)] = suf
									output.append(opt)
	return output

def create_irregular(form):
	global POSSIBLE_POS_IRREG
	anIrr = IrrC()
	POSSIBLE_POS = POSSIBLE_POS_IRREG
	anIrr.FORM = form
	for i in range(len(POSSIBLE_POS)):
		print str(i) + ': ' + POSSIBLE_POS[i][0]
	sel = -1
	while sel not in range(len(POSSIBLE_POS)):
		sel = raw_input('Which of the above POS tags is correct for this root?')
		if sel.isdigit():
			sel = int(sel)
	anIrr.POS = POSSIBLE_POS[sel][0]
	if POSSIBLE_POS[sel][1] == 'UNINFLECTED':
		anIrr.LEMMA = form
	else:
		print form
		sel2 = '123455677asd'
		while sel2 not in form:
			sel2 = raw_input('What is the lemma of this word?')
			if sel2 == '':
				sel2 = '123455677asd'
		anIrr.LEMMA = sel2
		for attnum in range(len(POSSIBLE_POS[sel][1])):
			print POSSIBLE_POS[sel][1][attnum][0] + ':\n'
			for i in range(len(POSSIBLE_POS[sel][1][attnum][1])):
				print str(i) + ': ' + POSSIBLE_POS[sel][1][attnum][1][i]
			sel2 = -1
			while sel2 not in range(len(POSSIBLE_POS[sel][1][attnum][1])):
				sel2 = raw_input('Which of the above POS tags is correct for this root?')
				if sel2.isdigit():
					sel2 = int(sel2)
			anIrr.__dict__[POSSIBLE_POS[sel][1][attnum][0]] = POSSIBLE_POS[sel][1][attnum][1][sel2]
	return anIrr

def create_root():
	global POSSIBLE_POS_ROOTS
	aRoot = RootC()
	for i in range(len(POSSIBLE_POS_ROOTS)):
		print str(i) + ': ' + POSSIBLE_POS_ROOTS[i][0]
	sel = -1
	while sel not in range(len(POSSIBLE_POS_ROOTS)):
		sel = raw_input('Which of the above POS tags is correct for this root?')
		if sel.isdigit():
			sel = int(sel)
	aRoot.POS = POSSIBLE_POS_ROOTS[sel][0]
	for attnum in range(len(POSSIBLE_POS_ROOTS[sel][1])):
		print POSSIBLE_POS_ROOTS[sel][1][attnum][0] + ':'
		if POSSIBLE_POS_ROOTS[sel][1][attnum][1][0] != 'ASK':
			for i in range(len(POSSIBLE_POS_ROOTS[sel][1][attnum][1])):
				print str(i) + ': ' + POSSIBLE_POS_ROOTS[sel][1][attnum][1][i]
			sel2 = -1
			while sel2 not in range(len(POSSIBLE_POS_ROOTS[sel][1][attnum][1])):
				sel2 = raw_input('Which of the above values is correct for this attribute?')
				if sel2.isdigit():
					sel2 = int(sel2)
			aRoot.__dict__[POSSIBLE_POS_ROOTS[sel][1][attnum][0]] = POSSIBLE_POS_ROOTS[sel][1][attnum][1][sel2]
		else:
			aRoot.__dict__[POSSIBLE_POS_ROOTS[sel][1][attnum][0]] = raw_input('What is the correct value for this attribute?')
	return aRoot
	
def pos_parse(text,roots,suffix,irr):
	tiernum = 0
	for suf in suffix:
		if suf.TIER.isdigit():
			if int(suf.TIER) > tiernum:
				tiernum = int(suf.TIER)
	nominals = ['N','ADJ']
	newtoks = []
	for token in text:
		newtok = []
		for wordnum in range(len(token.split(' '))):
			aword = Word()
			aword.META = {}
			if '_' in token.split(' ')[wordnum]:
				aword.ORTHO = token.split(' ')[wordnum].split('_')[0]
				aword.POS = token.split(' ')[wordnum].split('_')[1]
			else:
				aword.POS = ''
				while aword.POS == '':
					aword.ORTHO = token.split(' ')[wordnum].rstrip()
					print 'Previous context: ' + sentence(token.split(' ')[:wordnum])
					print 'Word: ' + token.split(' ')[wordnum]
					print 'Following context: ' + sentence(token.split(' ')[wordnum:])
					irrlist = []
					foundlist = []
					for irreg in irr:
						if token.split(' ')[wordnum] == irreg.FORM:
							irrlist.append(irreg)
					if irrlist != []:
						print 'IRREGULAR'
						suf = SuffixC()
						suf.FORM = 'NONE'
						suf.POS = 'NONE'
						irrlist.append(suf)
						form = token.split(' ')[wordnum]
						for irrnum in range(len(irrlist)):
							if irrlist[irrnum].POS == 'NONE':
								print str(irrnum) + ': NONE OF THE ABOVE'
							else:
								print str(irrnum) + ': ' + object_out(irrlist[irrnum])
						sel = -1
						while sel not in range(len(irrlist)):
							sel = raw_input('Which of the above parses is correct for this word?')
							if sel.isdigit():
								sel = int(sel)
						if irrlist[sel].POS != 'NONE':
							aword.META['LEMMA'] = irrlist[sel].LEMMA
							aword.POS = irrlist[sel].POS
							if hasattr(irrlist[sel],'GENDER'):
								aword.META['GENDER'] = irrlist[sel].GENDER
							if hasattr(irrlist[sel],'CASE'):
								aword.META['CASE'] = irrlist[sel].CASE
							if hasattr(irrlist[sel],'NUMBER'):
								aword.META['NUMBER'] = irrlist[sel].NUMBER
							if hasattr(irrlist[sel],'DEGREE'):
								aword.META['DEGREE'] = irrlist[sel].DEGREE
							if hasattr(irrlist[sel],'TENSE'):
								aword.META['TENSE'] = irrlist[sel].TENSE
							if hasattr(irrlist[sel],'MOOD'):
								aword.META['MOOD'] = irrlist[sel].MOOD
							if hasattr(irrlist[sel],'ASPECT'):
								aword.META['ASPECT'] = irrlist[sel].ASPECT
							if hasattr(irrlist[sel],'VOICE-MORPH'):
								aword.META['VOICE-MORPH'] = irrlist[sel].VOICE-MORPH
							if hasattr(irrlist[sel],'VOICE-SEMANTIC'):
								aword.META['VOICE-SEMANTIC'] = irrlist[sel].VOICE-SEMANTIC
							if hasattr(irrlist[sel],'PERSON'):
								aword.META['PERSON'] = irrlist[sel].PERSON
							if hasattr(irrlist[sel],'PERSON-AGR'):
								aword.META['PERSON-AGR'] = irrlist[sel].PERSON-AGR
							if hasattr(irrlist[sel],'NUMBER-AGR'):
								aword.META['NUMBER-AGR'] = irrlist[sel].NUMBER-AGR
							newtok.append(aword)
							break
					foundlist = tiersearch(token.split(' ')[wordnum].rstrip(), tiernum, 1, suffix, roots)
					print foundlist
					if foundlist != []:
						print 'FOUND ROOT'
						anOut = TierSearchOutput
						anOut.STEM = 'NONE'
						foundlist.append(anOut)
						for parsenum in range(len(foundlist)):
							if foundlist[parsenum].STEM == 'NONE':
								print str(parsenum) + ': NONE OF THE ABOVE'
							else:
								print str(parsenum) + ': ' + foundlist[parsenum].STEM + '-, ' + object_out(foundlist[parsenum])
						sel = -1
						while sel not in range(len(foundlist)):
							sel = raw_input('Which of the above parses is correct for this word?')
							if sel.isdigit():
								sel = int(sel)
						if foundlist[sel].STEM != 'NONE':
							try:
								aword.META['LEMMA'] = foundlist[sel].LEMMA
							except:
								aword.META['LEMMA'] = foundlist[sel].STEM + '-'
							assigned = 0
							for atr in foundlist[sel].__dict__:
								if 'Tier' in atr:
									for atr2 in foundlist[sel].__dict__[atr].__dict__:
										if atr2 == 'PREVIOUS_POS':
											aword.POS = foundlist[sel].__dict__[atr].POS
											assigned = 1
							if assigned == 0:
								aword.POS = roots[foundlist[sel].STEM].POS
							for tier in range(tiernum,0,-1):
								try:
									if hasattr(foundlist[sel].__dict__['Tier' + str(tier)],'GENDER'):
										aword.META['GENDER'] = foundlist[sel].__dict__['Tier' + str(tier)].GENDER
									if hasattr(foundlist[sel].__dict__['Tier' + str(tier)],'CASE'):
										aword.META['CASE'] = foundlist[sel].__dict__['Tier' + str(tier)].CASE
									if hasattr(foundlist[sel].__dict__['Tier' + str(tier)],'NUMBER'):
										aword.META['NUMBER'] = foundlist[sel].__dict__['Tier' + str(tier)].NUMBER
									if hasattr(foundlist[sel].__dict__['Tier' + str(tier)],'DEGREE'):
										aword.META['DEGREE'] = foundlist[sel].__dict__['Tier' + str(tier)].DEGREE
									if hasattr(foundlist[sel].__dict__['Tier' + str(tier)],'TENSE'):
										aword.META['TENSE'] = foundlist[sel].__dict__['Tier' + str(tier)].TENSE
									if hasattr(foundlist[sel].__dict__['Tier' + str(tier)],'MOOD'):
										aword.META['MOOD'] = foundlist[sel].__dict__['Tier' + str(tier)].MOOD
									if hasattr(foundlist[sel].__dict__['Tier' + str(tier)],'ASPECT'):
										aword.META['ASPECT'] = foundlist[sel].__dict__['Tier' + str(tier)].ASPECT
									if hasattr(foundlist[sel].__dict__['Tier' + str(tier)],'VOICE-MORPH'):
										aword.META['VOICE-MORPH'] = foundlist[sel].__dict__['Tier' + str(tier)].VOICE-MORPH
									if hasattr(foundlist[sel].__dict__['Tier' + str(tier)],'VOICE-SEMANTIC'):
										aword.META['VOICE-SEMANTIC'] = foundlist[sel].__dict__['Tier' + str(tier)].VOICE-SEMANTIC
									if hasattr(foundlist[sel].__dict__['Tier' + str(tier)],'PERSON'):
										aword.META['PERSON'] = foundlist[sel].__dict__['Tier' + str(tier)].PERSON
									if hasattr(foundlist[sel].__dict__['Tier' + str(tier)],'PERSON-AGR'):
										aword.META['PERSON-AGR'] = foundlist[sel].__dict__['Tier' + str(tier)].PERSON-AGR
									if hasattr(foundlist[sel].__dict__['Tier' + str(tier)],'NUMBER-AGR'):
										aword.META['NUMBER-AGR'] = foundlist[sel].__dict__['Tier' + str(tier)].NUMBER-AGR
								except:
									continue
							newtok.append(aword)
							break
					options = ['Y','N']
					sel = 1
					while sel not in options:
						sel = raw_input('Is this word irregular or uninflected [Y/N]?')[0].capitalize()
					if sel == 'Y':
						irr.append(create_irregular(aword.ORTHO))
						aword.META['LEMMA'] = irr[-1].LEMMA
						aword.POS = irr[-1].POS
						if hasattr(irr[-1],'GENDER'):
							aword.META['GENDER'] = irr[-1].GENDER
						if hasattr(irr[-1],'CASE'):
							aword.META['CASE'] = irr[-1].CASE
						if hasattr(irr[-1],'NUMBER'):
							aword.META['NUMBER'] = irr[-1].NUMBER
						if hasattr(irr[-1],'DEGREE'):
							aword.META['DEGREE'] = irr[-1].DEGREE
						if hasattr(irr[-1],'TENSE'):
							aword.META['TENSE'] = irr[-1].TENSE
						if hasattr(irr[-1],'MOOD'):
							aword.META['MOOD'] = irr[-1].MOOD
						if hasattr(irr[-1],'ASPECT'):
							aword.META['ASPECT'] = irr[-1].ASPECT
						if hasattr(irr[-1],'VOICE-MORPH'):
							aword.META['VOICE-MORPH'] = irr[-1].VOICE-MORPH
						if hasattr(irr[-1],'VOICE-SEMANTIC'):
							aword.META['VOICE-SEMANTIC'] = irr[-1].VOICE-SEMANTIC
						if hasattr(irr[-1],'PERSON'):
							aword.META['PERSON'] = irr[-1].PERSON
						if hasattr(irr[-1],'PERSON-AGR'):
							aword.META['PERSON-AGR'] = irr[-1].PERSON-AGR
						if hasattr(irr[-1],'NUMBER-AGR'):
							aword.META['NUMBER-AGR'] = irr[-1].NUMBER-AGR
						newtok.append(aword)
						break
					else:	
						sel = '123455677asd'
						while sel not in token.split(' ')[wordnum]:
							sel = raw_input('What is the stem of this word [Select NONE, if no new stem]?')
							print sel.upper()
							print sel.upper() == 'NONE'
							if sel == '':
								sel = '123455677asd'
							elif sel.upper() == 'NONE':
								break
						if sel.upper() != 'NONE':
							roots[sel] = create_root()
						foundlist = tiersearch(token.split(' ')[wordnum].rstrip(), tiernum, 1, suffix, roots)
						if foundlist != []:
							anOut = TierSearchOutput
							anOut.STEM = 'NONE'
							foundlist.append(anOut)
							for parsenum in range(len(foundlist)):
								if foundlist[parsenum].STEM == 'NONE':
									print str(parsenum) + ': NONE OF THE ABOVE'
								else:
									print str(parsenum) + ': ' + foundlist[parsenum].STEM + '-, ' + object_out(foundlist[parsenum])
							sel = -1
							while sel not in range(len(foundlist)):
								sel = raw_input('Which of the above parses is correct for this word?')
								if sel.isdigit():
									sel = int(sel)
							if foundlist[sel].STEM != 'NONE':
								try:
									aword.META['LEMMA'] = foundlist[sel].LEMMA
								except:
									aword.META['LEMMA'] = foundlist[sel].STEM + '-'
								assigned = 0
								for atr in foundlist[sel].__dict__:
									if 'Tier' in atr:
										for atr2 in foundlist[sel].__dict__[atr].__dict__:
											if atr2 == 'PREVIOUS_POS':
												aword.POS = foundlist[sel].__dict__[atr].POS
												assigned = 1
								if assigned == 0:
									aword.POS = roots[foundlist[sel].STEM].POS
								for tier in range(tiernum,0,-1):
									try:
										if hasattr(foundlist[sel].__dict__['Tier' + str(tier)],'GENDER'):
											aword.META['GENDER'] = foundlist[sel].__dict__['Tier' + str(tier)].GENDER
										if hasattr(foundlist[sel].__dict__['Tier' + str(tier)],'CASE'):
											aword.META['CASE'] = foundlist[sel].__dict__['Tier' + str(tier)].CASE
										if hasattr(foundlist[sel].__dict__['Tier' + str(tier)],'NUMBER'):
											aword.META['NUMBER'] = foundlist[sel].__dict__['Tier' + str(tier)].NUMBER
										if hasattr(foundlist[sel].__dict__['Tier' + str(tier)],'DEGREE'):
											aword.META['DEGREE'] = foundlist[sel].__dict__['Tier' + str(tier)].DEGREE
										if hasattr(foundlist[sel].__dict__['Tier' + str(tier)],'TENSE'):
											aword.META['TENSE'] = foundlist[sel].__dict__['Tier' + str(tier)].TENSE
										if hasattr(foundlist[sel].__dict__['Tier' + str(tier)],'MOOD'):
											aword.META['MOOD'] = foundlist[sel].__dict__['Tier' + str(tier)].MOOD
										if hasattr(foundlist[sel].__dict__['Tier' + str(tier)],'ASPECT'):
											aword.META['ASPECT'] = foundlist[sel].__dict__['Tier' + str(tier)].ASPECT
										if hasattr(foundlist[sel].__dict__['Tier' + str(tier)],'VOICE-MORPH'):
											aword.META['VOICE-MORPH'] = foundlist[sel].__dict__['Tier' + str(tier)].VOICE-MORPH
										if hasattr(foundlist[sel].__dict__['Tier' + str(tier)],'VOICE-SEMANTIC'):
											aword.META['VOICE-SEMANTIC'] = foundlist[sel].__dict__['Tier' + str(tier)].VOICE-SEMANTIC
										if hasattr(foundlist[sel].__dict__['Tier' + str(tier)],'PERSON'):
											aword.META['PERSON'] = foundlist[sel].__dict__['Tier' + str(tier)].PERSON
										if hasattr(foundlist[sel].__dict__['Tier' + str(tier)],'PERSON-AGR'):
											aword.META['PERSON-AGR'] = foundlist[sel].__dict__['Tier' + str(tier)].PERSON-AGR
										if hasattr(foundlist[sel].__dict__['Tier' + str(tier)],'NUMBER-AGR'):
											aword.META['NUMBER-AGR'] = foundlist[sel].__dict__['Tier' + str(tier)].NUMBER-AGR
									except:
										continue
								newtok.append(aword)
								break
		newtoks.append(newtok)				
	output = [newtoks,roots,suffix,irr]
	return output
				
				
for arg in sys.argv:
	if arg[-3:] == 'txt':
		oldfile = open(arg)
		lines = oldfile.readlines()
		suffixfile = open("./Suffix.txt")
		irrfile = open("./Irregular.txt")
		rootfile = open("./Roots.txt")
		roots = parse_root(rootfile.readlines())
		suffix = parse_suffix(suffixfile.readlines())
		irr = parse_irregular(irrfile.readlines())
		suffixfile.close()
		irrfile.close()
		rootfile.close()
		oldfile.close()
		tagger_output = pos_parse(lines,roots,suffix,irr)
		rootfile = open("./Roots.txt",'w')
		for ppos in POSSIBLE_POS_ROOTS:
			output = 'POS:' + ppos[0]
			for att in ppos[1]:
				output = output + ' ' + att[0] + ':'
				for value in att[1]:
					output = output + value + '|'
				output = output.rstrip('|')
			rootfile.write(output + '\n')
		rootfile.write('###\n')
		for root in tagger_output[1]:
			output = root
			for att in tagger_output[1][root].__dict__:
				output = output + ' ' + att + ':' + tagger_output[1][root].__dict__[att]
			rootfile.write(output + '\n')
		rootfile.close()
		irrfile = open("./Irregular.txt",'w')
		for ppos in POSSIBLE_POS_IRREG:
			output = 'POS:' + ppos[0]
			if ppos[1] == 'UNINFLECTED':
				irrfile.write(output + '\n')
				continue
			else:
				for att in ppos[1]:
					output = output + ' ' + att[0] + ':'
					for value in att[1]:
						output = output + value + '|'
					output = output.rstrip('|')
			irrfile.write(output + '\n')
		irrfile.write('###\n')
		for irreg in tagger_output[3]:
			output = irreg.FORM + ' ' + irreg.LEMMA
			for att in irreg.__dict__:
				if att not in ['FORM','LEMMA']:
					output = output + ' ' + att + ':' + irreg.__dict__[att]
			irrfile.write(output + '\n')
		irrfile.close()
		newfile = open(str(arg[:-3]+'psd'),'w')
		for token in tagger_output[0]:
			toktext = ''
			for word in token:
				toktext = toktext + '(' + word.POS + ' (ORTHO ' + word.ORTHO + ') (META '
				for att in word.META.keys():
					if att[0].isalpha():
						toktext = toktext + '(' + att + ' ' + word.META[att] + ') '
				toktext = toktext.rstrip() + ')) '
			newfile.write(toktext + '\n\n')
		newfile.close()
