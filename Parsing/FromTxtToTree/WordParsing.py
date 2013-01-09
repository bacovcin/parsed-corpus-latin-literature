import MySQLdb
import MySQLdb.cursors 
import string
from nltk.tree import *
import sys
from Tkinter import *
import ttk
import Tkinter

def exit():
    pass

class meta(object):
	def __init__(self):
		self.LEMMA = ''
		self.ID = -1
		self.RELATION = ''
		self.HEAD = -1
		
class Namespace: pass

def Set_Token_Text(listofwords,value_word,current_word):
	if current_word >= 8:
		if current_word <= len(listofwords)-9:
			if current_word - value_word <= 8 and current_word - value_word >= -8:
				tokentext = ' '.join(listofwords[1+current_word-8:value_word])+' '+listofwords[value_word].upper()+' '+' '.join(listofwords[value_word+1:current_word+8])
			else:
				tokentext = ' '.join(listofwords[1+current_word - 8:current_word + 8])
		else:
			if current_word-(8+(8-(len(listofwords)-(1+current_word)))) >= 0:
				if current_word - value_word <= (8+(8-(len(listofwords)-(1+current_word)))) and current_word - value_word >= -8:
					tokentext = ' '.join(listofwords[1+current_word-(8+(8-(len(listofwords)-(1+current_word)))):value_word])+' '+listofwords[value_word].upper()+' '+' '.join(listofwords[1+value_word:])
				else:
					tokentext = ' '.join(listofwords[1+current_word-(8+(8-(len(listofwords)-(1+current_word)))):])
			else:
				tokentext = ' '.join(listofwords[:value_word])+' '+listofwords[value_word].upper()+' '.join(listofwords[1+value_word:])
	else:
		if current_word <= len(listofwords)-9:
			if current_word+(8+(8-current_word)) <= len(listofwords)-1:
				if current_word - value_word <= 8 and current_word - value_word >= -(8+(8-current_word)):
					tokentext = ' '.join(listofwords[:value_word])+' '+listofwords[value_word].upper()+' '+' '.join(listofwords[1+value_word:current_word+(8+(8-current_word))])
				else:
					tokentext = ' '.join(listofwords[:current_word+(8+(8-current_word))])
			else:
				tokentext = ' '.join(listofwords[:value_word])+' '+listofwords[value_word].upper()+' '+' '.join(listofwords[1+value_word:])
		else:
			tokentext = ' '.join(listofwords[:value_word])+' '+listofwords[value_word].upper()+' '+' '.join(listofwords[1+value_word:])
	return tokentext
	
def Confirm_Sep(word):
	confirm = Namespace()
	confirm.var = Namespace()
	def Confirm():
		confirm.var = 'T'
		root.destroy()
		return confirm
	def Deny():
		confirm.var = 'F'
		root.destroy()
		return confirm
	root = Tk()
	root.title('Seperation Confirmation')
	mainframe = ttk.Frame(root)
	mainframe.grid(column=0,row=0,sticky=(N,W,E,S))
	mainframe.columnconfigure(0,weight=1)
	mainframe.rowconfigure(0,weight=1)
	ttk.Label(mainframe,text=word,justify='center').grid(column=1,row=1,columnspan=2)
	ttk.Button(mainframe,text='Confirm',command=Confirm).grid(column=1,row=2,sticky=(W,E))
	ttk.Button(mainframe,text='Deny',command=Deny).grid(column=2,row=2,sticky=(W,E))
	root.protocol("WM_DELETE_WINDOW", exit)
	root.mainloop()
	return confirm.var

def Find_POS(morph, lemma, word):
	Q = ['omnis', 'multus']
	WAdv = ['quando','quo','unde','ubi','quam','cur']
	WPro = ['qui','quis']
	WQ = ['num','utrum']
	ConjList = ['et','ve','que','ne','vel','at','ac','atque','aut','nec']
	if morph[0] == 'n':
		word.POS = 'N'
	elif morph[0] == 'r':
		word.POS = 'P'
	elif morph[0] == 'v':
		if lemma == 'sum':
			word.POS = 'BE'
		else:
			word.POS = 'VB'
	elif morph[0] == 't':
		if lemma == 'sum':
			word.POS = 'BE-ADJ'
		else:
			word.POS = 'VB-ADJ'
	elif morph[0] == 'a':
		if lemma in Q:
			word.POS = 'Q'
		else:
			word.POS = 'ADJ'
	elif morph[0] == 'd':
		if lemma in WQ:
			word.POS = 'WQ'
		elif lemma in WAdv:
			word.POS = 'WADV'
		elif lemma == 'non':
			word.POS = 'NEG'
		else:
			word.POS = 'ADV'
	elif morph[0] == 'c':
		if lemma in ConjList:
			word.POS = 'CONJ'
		else:
			word.POS = 'C'
	elif morph[0] == 'p':
		if lemma in WPro:
			word.POS = 'WPRO'
		else:
			word.POS = 'PRO'
	elif morph[0] == 'm':
		word.POS = 'NUM'
	elif morph[0] in ['i','e']:
		word.POS = 'INTJ'
	elif morph[0] == 'u':
		word.POS = '.'
	if morph[1] != '-':
		person = {'1':'FIRST','2':'SECOND','3':'THIRD'}
		word.META.PERSON = person[morph[1]]
	if morph[2] != '-':
		number = {'s':'SINGULAR','p':'PLURAL'}
		word.META.NUMBER = number[morph[2]]
	if morph[3] != '-':
		tense = {'p':'PRESENT','i':'PAST','r':'PRESENT','l':'PAST','t':'FUTURE','f':'FUTURE'}
		aspect = {'p':'IMPERFECT','i':'IMPERFECT','r':'PERFECT','l':'PERFECT','t':'PERFECT','f':'IMPERFECT'}
		word.META.TENSE = tense[morph[3]]
		word.META.ASPECT = aspect[morph[3]]
	if morph[4] != '-':
		mood = {'i':'INDICATIVE','s':'SUBJUNCTIVE','n':'INFINITIVE','m':'IMPERATIVE','p':'PARTICIPLE','d':'GERUND','g':'GERUNDIVE','u':'SUPINE'}
		word.META.MOOD = mood[morph[4]]
	if morph[5] != '-':
		voice = {'a':'ACTIVE','p':'PASSIVE'}
		word.META.VOICE = voice[morph[5]]
	if morph[6] != '-':
		gender = {'m':'MASCULINE','f':'FEMININE','n':'NEUTER'}
		word.META.GENDER = gender[morph[6]]
	if morph[7] != '-':
		case = {'n':'nominative'.upper(),'g':'genitive'.upper(),'d':'dative'.upper(),'a':'accusative'.upper(),'b':'ablative'.upper(),'v':'vocative'.upper(),'l':'locative'.upper()}
		word.META.CASE = case[morph[7]]
	if morph[8] != '-':
		degree = {'c':'COMPARATIVE','s':'SUPERLATIVE'}
		word.META.DEGREE = degree[morph[8]]
	return word
	
def Get_Relation_Options(word):
	verbs = ['VB','BE']
	participles = ['VB-ADJ','BE-ADJ']
	nominals = ['N','PRO']
	relations = []
	if word.POS == 'INTJ':
		relations = ['NULL','INTJP']
	elif word.POS == 'NUM':
		relations = ['NULL','NUMP']
	elif word.POS == '.':
		relations = ['NULL','CONJP']
	elif word.POS == 'CONJ':
		relations = ['NULL','CONJP']
	elif word.POS == 'ADV':
		relations = ['NULL','ADVP','ADVP-LOC','ADVP-TMP','ADVP-DIR']
	elif word.POS == 'ADJ':
		relations = ['NULL','ADJP','ADJP-LOC','ADJP-SPR']
		if word.META.CASE == 'NOMINATIVE':
			relations = relations + ['NP-SBJ','NP-PRD','NP-PRN','NP']
		elif word.META.CASE == 'GENITIVE':
			relations = relations + ['NP-POS','NP-PRN','NP','NP-COM','NP']
		elif word.META.CASE == 'DATIVE':
			relations = relations + ['NP-OB2','NP-PRN','NP','NP-COM','NP-DIR','NP']
		elif word.META.CASE == 'ACCUSATIVE':
			relations = relations + ['NP-OB1','NP-PRN','NP','NP-SPR','NP-COM','NP-MSR','NP-DIR','NP']
		elif word.META.CASE == 'ABLATIVE':
			relations = relations + ['NP','NP-ADV','NP-TMP','NP-LOC','NP']
		elif word.META.CASE == 'VOCATIVE':
			relations = relations + ['NP-VOC','NP']
		elif word.META.CASE == 'LOCATIVE':
			relations = relations + ['NP-LOC','NP']
	elif word.POS == 'Q':
		relations = ['NULL','QP']
	elif word.POS in nominals:
		if word.META.CASE == 'NOMINATIVE':
			relations = ['NP-SBJ','NP-PRD','NP-PRN','NP']
		elif word.META.CASE == 'GENITIVE':
			relations = ['NP-POS','NP-PRN','NP','NP-COM','NP']
		elif word.META.CASE == 'DATIVE':
			relations = ['NP-OB2','NP-PRN','NP','NP-COM','NP-DIR','NP']
		elif word.META.CASE == 'ACCUSATIVE':
			relations = ['NP-OB1','NP-PRN','NP','NP-SPR','NP-COM','NP-MSR','NP-DIR','NP']
		elif word.META.CASE == 'ABLATIVE':
			relations = ['NP','NP-ADV','NP-TMP','NP-LOC','NP']
		elif word.META.CASE == 'VOCATIVE':
			relations = ['NP-VOC','NP']
		elif word.META.CASE == 'LOCATIVE':
			relations = ['NP-LOC','NP']
	elif word.POS in participles:
		relations = ['IP-PPL','IP-SMC']
		if word.META.CASE == 'NOMINATIVE':
			relations = relations + ['NP-SBJ','NP-PRD','NP-PRN','NP']
		elif word.META.CASE == 'GENITIVE':
			relations = relations + ['NP-POS','NP-PRN','NP','NP-COM','NP']
		elif word.META.CASE == 'DATIVE':
			relations = relations + ['NP-OB2','NP-PRN','NP','NP-COM','NP-DIR','NP']
		elif word.META.CASE == 'ACCUSATIVE':
			relations = relations + ['NP-OB1','NP-PRN','NP','NP-SPR','NP-COM','NP-MSR','NP-DIR','NP']
		elif word.META.CASE == 'ABLATIVE':
			relations = relations + ['IP-PPL-ABS','NP','NP-ADV','NP-TMP','NP-LOC','NP']
		elif word.META.CASE == 'VOCATIVE':
			relations = relations + ['NP-VOC','NP']
		elif word.META.CASE == 'LOCATIVE':
			relations = relations + ['NP-LOC','NP']
	elif word.POS == 'P':
		relations = ['PP','WPP']
	elif word.POS == 'WQ':
		relations = ['NULL']
	elif word.POS == 'WPRO':
		if word.META.CASE == 'NOMINATIVE':
			relations = ['WNP-SBJ','WNP-PRD','WNP-PRN']
		elif word.META.CASE == 'GENITIVE':
			relations = ['WNP-POS','WNP-PRN','WNP','WNP-COM']
		elif word.META.CASE == 'DATIVE':
			relations = ['WNP-OB2','WNP-PRN','WNP','WNP-COM','WNP-DIR']
		elif word.META.CASE == 'ACCUSATIVE':
			relations = ['WNP-OB1','WNP-PRN','WNP','WNP-SPR','WNP-COM','WNP-MSR','WNP-DIR']
		elif word.META.CASE == 'ABLATIVE':
			relations = ['WNP','WNP-ADV','WNP-TMP','WNP-LOC']
		elif word.META.CASE == 'VOCATIVE':
			relations = ['WNP-VOC']
		elif word.META.CASE == 'LOCATIVE':
			relations = ['WNP-LOC']
	elif word.POS == 'WADV':
		relations = ['WADVP']
	elif word.POS == 'C':
		relations = ['CP-ADV','CP-CMP','CP-THT']
	elif word.POS in verbs:
		if word.META.MOOD in ['INDICATIVE','SUBJUNCTIVE']:
			relations = ['IP-MAT','CP-REL','CP-FRL','CP-CAR','CP-THT','IP-SUB']
		elif word.META.MOOD == 'IMPERATIVE':
			relations = ['IP-IMP']
		elif word.META.MOOD == 'INFINITIVE':
			relations = ['IP-INF','CP-EOP', 'IP-INF-PRP','CP-DEG','IP-INF-DEG','IP-INF-ADT']
	else:
		print 'ERROR, ERROR, POS not in list!'
	return relations
	
def Choose_Lemma(lemmas, words, current_word):
	word_placement = Namespace()
	word_placement.special = current_word
	word_placement.current = current_word
	def Increment_Token_Text():
		if word_placement.current < 8:
			word_placement.current = 8
		if word_placement.current != len(listofwords)-1:
			word_placement.current = word_placement.current + 1
			tokentext.set(Set_Token_Text(listofwords,word_placement.special,word_placement.current))
		return()
	def Decrease_Token_Text():
		if word_placement.current > len(listofwords)-9:
			word_placement.current = len(listofwords)-9
		if word_placement.current != 0:
			word_placement.current = word_placement.current - 1
			tokentext.set(Set_Token_Text(listofwords,word_placement.special,word_placement.current))
		return()
	root = Tk()
	root.title('Choose Lemma')
	mainframe = ttk.Frame(root,padding='5')
	mainframe.grid(column=0,row=1,sticky=(W,E,S))
	mainframe.columnconfigure(0,weight=1)
	mainframe.rowconfigure(0,weight=1)
	topframe = ttk.Frame(root,padding='5')
	topframe.grid(column=0,row=0,sticky=(W,E,N))
	topframe.columnconfigure(0,weight=1)
	topframe.rowconfigure(0,weight=1)
	listofwords = []
	for word in words:
		listofwords.append(word.ORTHO)
	tokentext = Tkinter.StringVar()
	tokentext.set(Set_Token_Text(listofwords,word_placement.special,word_placement.current))
	tokenlabel = ttk.Label(topframe,textvariable=tokentext,justify='center')
	tokenlabel.grid(column=0,row=0,columnspan=3,sticky=(N))
	ttk.Button(topframe,text='<',command=Decrease_Token_Text).grid(column=0,row=1,sticky=(W))
	ttk.Button(topframe,text='>',command=Increment_Token_Text).grid(column=2,row=1,sticky=(E))
	
	lemma = Tkinter.StringVar()
	lemma_choices = []
	
	definition = Tkinter.StringVar()
	definition.set('')
	
	def Scroll_over(event):
		definition.set(lemmas[widgetnames[event.widget.__dict__['_name']]]['def'])
	
	for l in lemmas.keys():
		lemma_choices.append(ttk.Radiobutton(mainframe, text=l, variable=lemma, value=l))
	
	widgetnames = {}
	for i in range(len(lemma_choices)):
		obj = lemma_choices[i]
		obj.pack()
		obj.bind('<Enter>',Scroll_over)
		widgetnames[obj.__dict__['_name']] = lemmas.keys()[i]
	
	ttk.Label(mainframe,text='Definition:').pack()
	ttk.Label(mainframe,textvariable=definition).pack()
	
	def Close():
		root.destroy()
	ttk.Button(mainframe,text='Confirm',command=Close).pack()
	
	root.mainloop()
	return lemma.get()

def Choose_Morph(morphs, words, current_word):
	word_placement = Namespace()
	word_placement.special = current_word
	word_placement.current = current_word
	def Increment_Token_Text():
		if word_placement.current < 8:
			word_placement.current = 8
		if word_placement.current != len(listofwords)-1:
			word_placement.current = word_placement.current + 1
			tokentext.set(Set_Token_Text(listofwords,word_placement.special,word_placement.current))
		return()
	def Decrease_Token_Text():
		if word_placement.current > len(listofwords)-9:
			word_placement.current = len(listofwords)-9
		if word_placement.current != 0:
			word_placement.current = word_placement.current - 1
			tokentext.set(Set_Token_Text(listofwords,word_placement.special,word_placement.current))
		return()
	root = Tk()
	root.title('Choose Morph')
	mainframe = ttk.Frame(root,padding='5')
	mainframe.grid(column=0,row=1,sticky=(W,E))
	mainframe.columnconfigure(0,weight=1)
	mainframe.rowconfigure(0,weight=1)
	topframe = ttk.Frame(root,padding='5')
	topframe.grid(column=0,row=0,sticky=(W,E,N))
	topframe.columnconfigure(0,weight=1)
	topframe.rowconfigure(0,weight=1)
	bottomframe = ttk.Frame(root,padding='5')
	bottomframe.grid(column=0,row=2,sticky=(W,E,S))
	bottomframe.columnconfigure(0,weight=1)
	bottomframe.rowconfigure(0,weight=1)
	listofwords = []
	for word in words:
		listofwords.append(word.ORTHO)
	tokentext = Tkinter.StringVar()
	tokentext.set(Set_Token_Text(listofwords,word_placement.special,word_placement.current))
	tokenlabel = ttk.Label(topframe,textvariable=tokentext,justify='center')
	tokenlabel.grid(column=0,row=0,columnspan=3,sticky=(N))
	ttk.Button(topframe,text='<',command=Decrease_Token_Text).grid(column=0,row=1,sticky=(W))
	ttk.Button(topframe,text='>',command=Increment_Token_Text).grid(column=2,row=1,sticky=(E))
	
	morph = Tkinter.StringVar()
	morph_choices = []
	for m in morphs:
		morph_choices.append(ttk.Radiobutton(mainframe, text=m, variable=morph, value=m))
	for obj in morph_choices:
		obj.pack()
	morph.set(morphs[0])
		
	ttk.Label(bottomframe,text = '1:\nn\tnoun\nv\tverb\nt\tparticiple\na\tadjective\nd\tadverb\nc\tconjunction\nr\tpreposition\np\tpronoun\nm\tnumeral\ni\tinterjection\ne\texclamation\nu\tpunctuation').grid(column=0,row=0,sticky=(N))
	ttk.Label(bottomframe,text = '2:\n1\tfirst person\n2\tsecond person\n3\tthird person').grid(column=1,row=0,sticky=(N))
	ttk.Label(bottomframe,text = '3:\ns\tsingular\np\tplural').grid(column=2,row=0,sticky=(N))
	ttk.Label(bottomframe,text = '4:\np\tpresent\ni\timperfect\nr\tperfect\nl\tpluperfect\nt\tfuture perfect\nf\tfuture').grid(column=3,row=0,sticky=(N))
	ttk.Label(bottomframe,text = '5:\ni\tindicative\ns\tsubjunctive\nn\tinfinitive\nm\timperative\np\tparticiple\nd\tgerund\ng\tgerundive\nu\tsupine').grid(column=0,row=1,sticky=(N))
	ttk.Label(bottomframe,text = '6:\na\tactive\np\tpassive').grid(column=1,row=1,sticky=(N))
	ttk.Label(bottomframe,text = '7:\nm\tmasculine\nf\tfeminine\nn\tneuter').grid(column=2,row=1,sticky=(N))
	ttk.Label(bottomframe,text = '8:\nn\tnominative\ng\tgenitive\nd\tdative\na\taccusative\nb\tablative\nv\tvocative\nl\tlocative').grid(column=3,row=1,sticky=(N))
	ttk.Label(bottomframe,text = '9:\nc\tcomparative\ns\tsuperlative').grid(column=4,row=1,sticky=(N))
	
	def Close():
		root.destroy()
	ttk.Button(mainframe,text='Confirm',command=Close).pack()
	root.mainloop()
	return morph.get()
	
def Syntactic_Dependencies(morph, lemma, words, current_word):
	word_placement = Namespace()
	word_placement.special = current_word
	word_placement.current = current_word
	def Increment_Token_Text():
		if word_placement.current < 8:
			word_placement.current = 8
		if word_placement.current != len(listofwords)-1:
			word_placement.current = word_placement.current + 1
			tokentext.set(Set_Token_Text(listofwords,word_placement.special,word_placement.current))
		return()
	def Decrease_Token_Text():
		if word_placement.current > len(listofwords)-9:
			word_placement.current = len(listofwords)-9
		if word_placement.current != 0:
			word_placement.current = word_placement.current - 1
			tokentext.set(Set_Token_Text(listofwords,word_placement.special,word_placement.current))
		return()
	our_word = words[current_word]
	our_word.META.LEMMA = lemma
	our_word = Find_POS(morph, lemma, our_word)
	relations = Get_Relation_Options(our_word)
	root = Tk()
	root.title('Syntactic Information')
	mainframe = ttk.Frame(root,padding='5')
	mainframe.grid(column=0,row=1,sticky=(W,E,S))
	mainframe.columnconfigure(0,weight=1)
	mainframe.rowconfigure(0,weight=1)
	topframe = ttk.Frame(root,padding='5')
	topframe.grid(column=0,row=0,sticky=(W,E,N))
	topframe.columnconfigure(0,weight=1)
	topframe.rowconfigure(0,weight=1)
	listofwords = []
	for word in words:
		listofwords.append(word.ORTHO)
	tokentext = Tkinter.StringVar()
	tokentext.set(Set_Token_Text(listofwords,word_placement.special,word_placement.current))
	tokenlabel = ttk.Label(topframe,textvariable=tokentext,justify='center')
	tokenlabel.grid(column=0,row=0,columnspan=3,sticky=(N))
	ttk.Button(topframe,text='<',command=Decrease_Token_Text).grid(column=0,row=1,sticky=(W))
	ttk.Button(topframe,text='>',command=Increment_Token_Text).grid(column=2,row=1,sticky=(E))
	ttk.Label(mainframe,text='HEAD:').grid(column=0,row=0,sticky=(W,E))
	ttk.Label(mainframe,text='RELATION:').grid(column=2,row=0,sticky=(W,E))
	
	def On_POS_Select(*args):
		pos_select.set(pos_list.curselection()[0])
		sel = pos_select.get()
		pos_selection_view.set(poses[int(sel)])
		
	if word.POS == '.':
		pos_select = Tkinter.StringVar()
		pos_selection_view = Tkinter.StringVar()
		poses = [',','.']
		pos_options = Tkinter.StringVar(value=poses)
		ttk.Label(mainframe,text='POS:').grid(column=4,row=0,sticky=(W,E))
		ttk.Label(mainframe,text='Current Selection:').grid(column=4,row=1,sticky=(W,E))
		ttk.Label(mainframe,textvariable=pos_selection_view).grid(column=5,row=1,sticky=(W,E))
		pos_list = Listbox(mainframe, height=16,listvariable=pos_options)
		pos_list.grid(column=4,row=2,sticky=(N,W,E,S))
		pos_list.bind('<<ListboxSelect>>', On_POS_Select)
	sentenceLevel = StringVar()
	sentenceLevel.set('0')
	def Set_Head_list_state():
		if sentenceLevel.get() == '0':
			head_list.config(state = NORMAL)
		else:
			head_list.config(state = DISABLED)
	headcheck = ttk.Checkbutton(mainframe, command=Set_Head_list_state, text='Sentence Level', variable=sentenceLevel)
	headcheck.grid(column=0,row=3,sticky=(W,E))
	head_list = Listbox(mainframe, height=16, listvariable=tokentext)
	head_list.grid(column=0,row=2,sticky=(N,W,E,S))
	head_s = ttk.Scrollbar(mainframe, orient=VERTICAL, command=head_list.yview)
	head_s.grid(column=1,row=2,sticky=(N,S,W))
	head_list.configure(yscrollcommand=head_s.set)
	head_list.selection_set(0)
	head_selection = Tkinter.StringVar()
	head_selection_view = Tkinter.StringVar()
	ttk.Label(mainframe,text='Current Selection:').grid(column=0,row=1,sticky=(W,E))
	ttk.Label(mainframe,textvariable=head_selection_view).grid(column=1,row=1,sticky=(W,E))
	def On_Head_Select(*args):
		head_selection.set(head_list.curselection()[0])
		sel = head_selection.get()
		head_selection_view.set(tokentext.get().split(' ')[int(sel)])
	head_list.bind('<<ListboxSelect>>', On_Head_Select)
	relation_selection = Tkinter.StringVar()
	relation_options = Tkinter.StringVar(value=relations)
	relation_list = Listbox(mainframe, height=16, listvariable = relation_options)
	relation_list.grid(column=2,row=2,sticky=(N,W,E,S))
	relation_s = ttk.Scrollbar(mainframe, orient=VERTICAL, command=relation_list.yview)
	relation_s.grid(column=3,row=2,sticky=(N,S,W))
	relation_list.configure(yscrollcommand=relation_s.set)
	relation_list.selection_set(0)
	relation_selection = Tkinter.StringVar()
	relation_selection_view = Tkinter.StringVar()
	ttk.Label(mainframe,text='Current Selection:').grid(column=2,row=1,sticky=(W,E))
	ttk.Label(mainframe,textvariable=relation_selection_view).grid(column=3,row=1,sticky=(W,E))
	def On_Relation_Select(*args):
		relation_selection.set(relation_list.curselection()[0])
		relation_selection_view.set(relations[int(relation_selection.get())])
	relation_list.bind('<<ListboxSelect>>', On_Relation_Select)
	try:
		if relations[0][:2] in ['IP','CP']:
			SPE_var = Tkinter.StringVar()
			SPEcheck = ttk.Checkbutton(mainframe, text='-SPE', variable=SPE_var)
			SPEcheck.grid(column=2,row=3,sticky=(W,E))
	except:
		pass
	def Close():
		if sentenceLevel.get() == '0':
			if len(words) < 16:
				our_word.META.HEAD = words[int(head_selection.get())].META.ID
			else:
				our_word.META.HEAD = words[int(head_selection.get())+(word_placement.current-8)].META.ID
		else:
			our_word.META.HEAD = 0
		try:
			if SPE_var.get() == '1':
				our_word.META.RELATION = relations[int(relation_selection.get())] + '-SPE'
			else:
				our_word.META.RELATION = relations[int(relation_selection.get())]
		except:
			our_word.META.RELATION = relations[int(relation_selection.get())]
		if word.POS == '.':
			our_word.POS = poses[int(pos_select.get())]
		root.destroy()
	ttk.Button(mainframe,text='Confirm',command=Close).grid(column=3,row=3,sticky=(W,E))
	root.mainloop()
	return our_word

class word_obj(object):
	def __init__(self):
		self.ORTHO = ''
		self.POS = ''
		self.META = meta()

def Create_Morphs(form,lemma,defin,cur,root):
	morphroot = Toplevel(root)
	morphroot.title('Create Morphcodes')
	
	morph_options = (('n','v','t','a','d','c','r','p','m','i','e','u'),('-','1','2','3'),('-','s','p'),('-','p','i','r','l','t','f'),('-','i','s','n','m','p','d','g','u'),('-','a','p'),('-','m','f','n'),('-','n','g','d','a','b','v','l'),('-','c','s'))
	
	mainframe = ttk.Frame(morphroot,padding='5')
	mainframe.grid(column=0,row=1,sticky=(W,E))
	mainframe.columnconfigure(0,weight=1)
	mainframe.rowconfigure(0,weight=1)
	topframe = ttk.Frame(morphroot,padding='5')
	topframe.grid(column=0,row=0,sticky=(W,E,N))
	topframe.columnconfigure(0,weight=1)
	topframe.rowconfigure(0,weight=1)
	bottomframe = ttk.Frame(morphroot,padding='5')
	bottomframe.grid(column=0,row=2,sticky=(W,E,S))
	bottomframe.columnconfigure(0,weight=1)
	bottomframe.rowconfigure(0,weight=1)
	
	ttk.Label(topframe,text='Form: '+form,justify='center').grid(column=0,row=0)
	ttk.Label(topframe,text='Lemma: '+lemma,justify='center').grid(column=1,row=0)
	ttk.Label(topframe,text='Short Def: '+defin,justify='center').grid(column=2,row=0)
		
	ttk.Label(bottomframe,text = '1:\nn\tnoun\nv\tverb\nt\tparticiple\na\tadjective\nd\tadverb\nc\tconjunction\nr\tpreposition\np\tpronoun\nm\tnumeral\ni\tinterjection\ne\texclamation\nu\tpunctuation').grid(column=0,row=0,sticky=(N))
	ttk.Label(bottomframe,text = '2:\n1\tfirst person\n2\tsecond person\n3\tthird person').grid(column=1,row=0,sticky=(N))
	ttk.Label(bottomframe,text = '3:\ns\tsingular\np\tplural').grid(column=2,row=0,sticky=(N))
	ttk.Label(bottomframe,text = '4:\np\tpresent\ni\timperfect\nr\tperfect\nl\tpluperfect\nt\tfuture perfect\nf\tfuture').grid(column=3,row=0,sticky=(N))
	ttk.Label(bottomframe,text = '5:\ni\tindicative\ns\tsubjunctive\nn\tinfinitive\nm\timperative\np\tparticiple\nd\tgerund\ng\tgerundive\nu\tsupine').grid(column=0,row=1,sticky=(N))
	ttk.Label(bottomframe,text = '6:\na\tactive\np\tpassive').grid(column=1,row=1,sticky=(N))
	ttk.Label(bottomframe,text = '7:\nm\tmasculine\nf\tfeminine\nn\tneuter').grid(column=2,row=1,sticky=(N))
	ttk.Label(bottomframe,text = '8:\nn\tnominative\ng\tgenitive\nd\tdative\na\taccusative\nb\tablative\nv\tvocative\nl\tlocative').grid(column=3,row=1,sticky=(N))
	ttk.Label(bottomframe,text = '9:\nc\tcomparative\ns\tsuperlative').grid(column=4,row=1,sticky=(N))
		
	morph_entries = [[Tkinter.StringVar(),Tkinter.StringVar(),Tkinter.StringVar(),Tkinter.StringVar(),Tkinter.StringVar(),Tkinter.StringVar(),Tkinter.StringVar(),Tkinter.StringVar(),Tkinter.StringVar()]]
	morph_widgets = [[]]
	for i in range(9):
		morph_entries[0][i].set(morph_options[i][0])
		morph_widgets[0].append(ttk.Combobox(mainframe,textvariable=morph_entries[0][i],width=1))
		morph_widgets[0][i]['values'] = morph_options[i]
		morph_widgets[0][i].grid(column=i,row=0, sticky=(E))
		morph_widgets[0][i].current(0)
	
	def Remove_Morph_Widget():
		if len(morph_widgets) > 1:
			for widget in morph_widgets[-1]:
				widget.destroy()
			del morph_widgets[-1]
			del morph_entries[-1]
	ttk.Button(topframe,text='Remove Morph',command=Remove_Morph_Widget).grid(column=0,row=1,sticky=(E))
	
	def Add_Morph_Widget():
		morph_entries.append([Tkinter.StringVar(),Tkinter.StringVar(),Tkinter.StringVar(),Tkinter.StringVar(),Tkinter.StringVar(),Tkinter.StringVar(),Tkinter.StringVar(),Tkinter.StringVar(),Tkinter.StringVar()])
		morph_widgets.append([])
		for i in range(9):
			morph_widgets[-1].append(ttk.Combobox(mainframe,textvariable=morph_entries[-1][i],width=1))
			morph_widgets[-1][i]['values'] = morph_options[i]
			if i == 0:
				morph_widgets[-1][i].grid(column=i,row=len(morph_widgets)-1, sticky=(E))
			else:
				morph_widgets[-1][i].grid(column=i,row=len(morph_widgets)-1, sticky=(W))
			morph_widgets[-1][i].current(0)
	ttk.Button(topframe,text='Add Morph',command=Add_Morph_Widget).grid(column=1,row=1)
	
	def Close():
		for entry in morph_widgets:
			amorph = ''
			for i in range(len(entry)):
				amorph = amorph + morph_options[i][entry[i].current()]
			cur.execute('INSERT INTO lat_parse (form,lemma_text,morph_code,lemma_short_def) VALUES (\''+form+'\',\''+lemma+'\',\''+amorph+'\',\''+defin+'\');')
		morphroot.destroy()
	ttk.Button(topframe,text='Confirm',command=Close).grid(column=2,row=1)

def Create_Lemmas(form,cur):
	lemmas = []
	root = Tk()
	root.title('')
	lemmaroot = Toplevel(root)
	lemmaroot.title('Create Lemmata')
	topleftframe = ttk.Frame(lemmaroot,padding='5')
	topleftframe.grid(column=0,row=1,sticky=(W,E,S))
	topleftframe.columnconfigure(0,weight=1)
	topleftframe.rowconfigure(0,weight=1)
	toprightframe = ttk.Frame(lemmaroot,padding='5')
	toprightframe.grid(column=1,row=1,sticky=(W,E,S))
	toprightframe.columnconfigure(0,weight=1)
	toprightframe.rowconfigure(0,weight=1)
	leftframe = ttk.Frame(lemmaroot,padding='5')
	leftframe.grid(column=0,row=2,sticky=(W,E,S))
	leftframe.columnconfigure(0,weight=1)
	leftframe.rowconfigure(0,weight=1)
	rightframe = ttk.Frame(lemmaroot,padding='5')
	rightframe.grid(column=1,row=2,sticky=(W,E,S))
	rightframe.columnconfigure(0,weight=1)
	rightframe.rowconfigure(0,weight=1)
	topframe = ttk.Frame(lemmaroot,padding='5')
	topframe.grid(column=0,row=0,columnspan=2,sticky=(W,E,N))
	topframe.columnconfigure(0,weight=1)
	topframe.rowconfigure(0,weight=1)
	bottomframe = ttk.Frame(lemmaroot,padding='5')
	bottomframe.grid(column=0,row=3,columnspan=2,sticky=(W,E,N))
	bottomframe.columnconfigure(0,weight=1)
	bottomframe.rowconfigure(0,weight=1)
	
	ttk.Label(topframe,text='Form',justify='right').grid(column=0,row=0,sticky=(E))
	ttk.Label(topframe,text=form,justify='left').grid(column=1,row=0,sticky=(W))
	ttk.Label(topleftframe,text='Lemmata:',justify='center').grid(column=0,row=0)
	ttk.Label(toprightframe,text='Short Defs:',justify='center').grid(column=0,row=0)
	
	
	lemma_entries = [[Tkinter.StringVar(),Tkinter.StringVar()]]
	lemma_widgets = [ttk.Entry(leftframe, textvariable = lemma_entries[0][0])]
	def_widgets = [ttk.Entry(rightframe, textvariable = lemma_entries[0][1])]
	lemma_widgets[0].pack()
	def_widgets[0].pack()
	
	def Remove_Lemma_Widget():
		if len(lemma_widgets) > 1:
			lemma_widgets[-1].destroy()
			del lemma_widgets[-1]
			def_widgets[-1].destroy()
			del def_widgets[-1]
			del lemma_entries[-1]
	ttk.Button(bottomframe,text='Remove Lemma',command=Remove_Lemma_Widget).grid(column=0,row=0)
	
	def Add_Lemma_Widget():
		lemma_entries.append((Tkinter.StringVar(),Tkinter.StringVar()))
		lemma_widgets.append(ttk.Entry(leftframe, textvariable = lemma_entries[-1][0]))
		lemma_widgets[-1].pack()
		def_widgets.append(ttk.Entry(rightframe, textvariable = lemma_entries[-1][1]))
		def_widgets[-1].pack()
	ttk.Button(bottomframe,text='Add Lemma',command=Add_Lemma_Widget).grid(column=1,row=0)
	
	def Set_Morphs():
		new_lemmas = []
		for lemma in lemma_entries:
			new_lemmas.append((lemma[0].get(),lemma[0].get()))
		for lemma in new_lemmas:
			Create_Morphs(form, lemma[0], lemma[1], cur, root)
		lemmaroot.destroy()
	ttk.Button(bottomframe,text='Confirm',command=Set_Morphs).grid(column=2,row=0)
	
	def Close():
		root.destroy()
	
	ttk.Button(root,text='Finish',command=Close).grid(column=0,row=0)
	root.mainloop()

def Get_Parses():
	db = MySQLdb.connect(host='localhost',user='pythoner',passwd='pythoner',db='perseus_data',cursorclass=MySQLdb.cursors.DictCursor)
	cur = db.cursor()
	return cur

def Output_Settings(settings):
	setfile = open('settings.cnf','w')
	for key in settings.keys():
		if key=='NEQUE':
			setfile.write('NEQUE:'+','.join(settings['NEQUE']))
	return

def Get_Settings():
	setfile = open('settings.cnf')
	settings = {}
	for line in setfile.readlines():
		if line.split(':')[0]=='NEQUE':
			settings['NEQUE'] = line.split(':')[1].split(',')
	return settings
	
def Find_Dependents(headword,words):
	deplist = []
	for i in range(len(words)):
		if words[i].META.HEAD == headword:
			deplist.append(i)
	return deplist

def WordsToTree(tree):
	newtree = Tree(tree.node, [])
	for child in tree:
		if isinstance(child,word_obj):
			wordtree = Tree(child.POS, [Tree('ORTHO', [child.ORTHO])])
			meta = Tree('META', [])
			for key in child.META.__dict__.keys():
				meta.append(Tree(key, [child.META.__dict__[key]]))
			wordtree.append(meta)
			newtree.append(wordtree)
		elif isinstance(child,Tree):
			newtree.append(WordsToTree(child))
		else:
			newtree.append(child)
	return newtree

def Phrase_Linearize(linlist):
	def Find_Lowest():
		lowest = 10000000000
		sel = -1
		for i in range(len(linlist)):
			if linlist[i][1][0] < lowest:
				lowest = linlist[i][1][0]
				sel = i
		return linlist.pop(sel)
	newlinlist = []
	while linlist != []:
		newlinlist.append(Find_Lowest())
	return newlinlist
	
def Find_Edges(tree):
	start = 100000000000000
	end = -1
	if isinstance(tree,word_obj):
		curid = tree.META.ID
		if curid < start:
			start = curid
		if curid > end:
			end = curid
	else:
		for child in tree:
			if isinstance(child,word_obj):
				curid = child.META.ID
				if curid < start:
					start = curid
				if curid > end:
					end = curid
			elif isinstance(child,Tree):
				new = Find_Edges(child)
				if new[0] < start:
					start = new[0]
				if new[1] > end:
					end = new[1]
	return [start,end]
	
def Find_Head(linlist,headid):
	for i in range(len(linlist)):
		if isinstance(linlist[i][0],word_obj):
			if linlist[i][0].META.ID == headid:
				return i
	raw_input('CANNOT FIND HEAD')

def Build_Tree(words,headword,running_index):
	deplist = Find_Dependents(words[headword].META.ID,words)
	if len(deplist) == 0:
		if words[headword].META.RELATION == 'NULL':
			return [words[headword],[],running_index]
		else:
			return [Tree(words[headword].META.RELATION,[words[headword]]),[],running_index]
	else:
		deptrees = []
		for dep in deplist:
			deptrees.append(Build_Tree(words,dep,running_index))
			running_index = deptrees[-1][2]
		returntree = [Tree(words[headword].META.RELATION,[words[headword]]),[]]
		newdeptrees = []
		if words[headword].META.RELATION[:2] in ['IP','CP']:
			for dt in deptrees:
				running_index = dt[2]
				newdeptrees.append(dt[0])
				for ichtree in dt[1]:
					newdeptrees.append(ichtree)
		else:
			for dt in deptrees:
				running_index = dt[2]
				newdeptrees.append(dt[0])
				for ichtree in dt[1]:
					returntree[1].append(ichtree)
		lintrees = [[words[headword],[words[headword].META.ID,words[headword].META.ID]]]
		for tree in newdeptrees:
			lintrees.append([tree,Find_Edges(tree)])
		lintrees = Phrase_Linearize(lintrees)
		linhead = Find_Head(lintrees,words[headword].META.ID)
		bbroken = 0
		wh = []
		conj = []
		for i in range(len(lintrees[:linhead])-1,-1,-1):
			if isinstance(lintrees[i][0],Tree):
				if lintrees[i][0].node[0] == 'W':
					lintrees[i][0].append(Tree('META',[Tree('INDEX',[running_index])]))
					wh.append(lintrees[i][0])
					returntree[0].insert(0,Tree(lintrees[i][0].node[1:],[Tree('META',[Tree('ALT-ORTHO',['*T*']),Tree('INDEX',[running_index])])]))
					wh[-1].node = lintrees[i][0].node.split('-')[0]
					running_index = running_index + 1
					continue
				elif lintrees[i][0].node == 'CONJP':
					conj.append(lintrees[i][0])
					continue
			if bbroken == 0:
				if lintrees[i][1][1] == lintrees[i+1][1][0]-1:
					returntree[0].insert(0,lintrees[i][0])
				else:
					bbroken = 1
					lintrees[i][0].append(Tree('META',[Tree('INDEX',[running_index])]))
					returntree[1].append(lintrees[i][0])
					returntree[0].insert(0,Tree(lintrees[i][0].node,[Tree('META',[Tree('ALT-ORTHO',['*ICH*']),Tree('INDEX',[running_index])])]))
					running_index = running_index + 1
			else:
				lintrees[i][0].append(Tree('META',[Tree('INDEX',[running_index])]))
				returntree[1].append(lintrees[i][0])
				returntree[0].insert(0,Tree(lintrees[i][0].node,[Tree('META',[Tree('ALT-ORTHO',['*ICH*']),Tree('INDEX',[running_index])])]))
				running_index = running_index + 1
		abroken = 0
		for i in range(linhead+1,(len(lintrees)),1):
			if isinstance(lintrees[i][0],Tree):
				if lintrees[i][0].node == 'CONJP':
					conj.append(lintrees[i][0])
					continue
			if abroken == 0:
				if lintrees[i][1][0] == lintrees[i-1][1][1]+1:
					returntree[0].append(lintrees[i][0])
				else:
					abroken = 1
					lintrees[i][0].append(Tree('META',[Tree('INDEX',[running_index])]))
					returntree[1].append(lintrees[i][0])
					returntree[0].append(Tree(lintrees[i][0].node,[Tree('META',[Tree('ALT-ORTHO',['*ICH*']),Tree('INDEX',[running_index])])]))
					running_index = running_index + 1
			else:
				lintrees[i][0].append(Tree('META',[Tree('INDEX',[running_index])]))
				returntree[1].append(lintrees[i][0])
				returntree[0].insert(0,Tree(lintrees[i][0].node,[Tree('META',[Tree('ALT-ORTHO',['*ICH*']),Tree('INDEX',[running_index])])]))
				running_index = running_index + 1
		if conj != []:
			newtree = Tree(returntree[0].node,[])
			returntree[0].node = returntree[0].node.split('-')[0]
			newtree.append(returntree[0])
			returntree[0] = newtree
			lintrees = [[returntree[0],Find_Edges(returntree[0])]]
			for tree in conj:
				lintrees.append([tree,Find_Edges(tree)])
			lintrees = Phrase_Linearize(lintrees)
			linhead = 0
			for i in range(len(lintrees)):
				if lintrees[i] == returntree[0]:
					linhead = i
			bbroken = 0
			for i in range(len(lintrees[:linhead])-1,-1,-1):
				if bbroken == 0:
					if lintrees[i][1][1] == lintrees[i+1][1][0]-1:
						returntree[0].insert(0,lintrees[i][0])
					else:
						bbroken = 1
						lintrees[i][0].append(Tree('META',[Tree('INDEX',[running_index])]))
						returntree[1].append(lintrees[i][0])
						returntree[0].insert(0,Tree(lintrees[i][0].node,[Tree('META',[Tree('ALT-ORTHO',['*ICH*']),Tree('INDEX',[running_index])])]))
						running_index = running_index + 1
				else:
					lintrees[i][0].append(Tree('META',[Tree('INDEX',[running_index])]))
					returntree[1].append(lintrees[i][0])
					returntree[0].insert(0,Tree(lintrees[i][0].node,[Tree('META',[Tree('ALT-ORTHO',['*ICH*']),Tree('INDEX',[running_index])])]))
					running_index = running_index + 1
			abroken = 0
			for i in range(linhead+1,(len(lintrees)),1):
				if abroken == 0:
					if lintrees[i][1][0] == lintrees[i-1][1][1]+1:
						returntree[0].append(lintrees[i][0])
					else:
						abroken = 1
						lintrees[i][0].append(Tree('META',[Tree('INDEX',[running_index])]))
						returntree[1].append(lintrees[i][0])
						returntree[0].append(Tree(lintrees[i][0].node,[Tree('META',[Tree('ALT-ORTHO',['*ICH*']),Tree('INDEX',[running_index])])]))
						running_index = running_index + 1
				else:
					lintrees[i][0].append(Tree('META',[Tree('INDEX',[running_index])]))
					returntree[1].append(lintrees[i][0])
					returntree[0].insert(0,Tree(lintrees[i][0].node,[Tree('META',[Tree('ALT-ORTHO',['*ICH*']),Tree('INDEX',[running_index])])]))
					running_index = running_index + 1
		if returntree[0].node[:2] == 'CP':
			if wh == []:
				newtree = Tree(returntree[0].node,[returntree[0]])
				newtree[0].node = 'IP-SUB'
				returntree[0] = newtree
			else:
				newtree_node = returntree[0].node
				returntree[0].node = 'IP-SUB'
				newtree = Tree(newtree_node,[wh[0],returntree[0]])
				returntree[0] = newtree
		returntree.append(running_index)
		#print WordsToTree(returntree[0])
		return returntree

def Syntax_Parse(words,idname,metadata,idnum):
	toklist = Find_Dependents(0,words)
	tokens = []
	for tokhead in toklist:
		running_index = 1
		atree = WordsToTree(Build_Tree(words,tokhead,running_index)[0])
		tokens.append(Tree('',[metadata,atree,Tree('ID',[idname.rstrip()+'.'+str(idnum)])]))
		idnum = idnum+1
	return [tokens,idnum]

def Parse_Letter(cur,words,idname,metadata,idnum):
	settings = Get_Settings()
	newwords = []
	tokens = []
	token = []
	synparse = [[]]
	for word in words:
		word = word.rstrip()
		try:
			if word[-1] in [',','.',';','?']:
				token.append(word[:-1])
				token.append(word[-1])
				if word[-1] in ['.','?']:
					tokens.append(token)
					token = []
			else:
				token.append(word)
		except:
			continue
	else:
		tokens.append(token)
	for token in tokens:	
		words = token
		newwords = []
		for word in words:
			if word[-2:] in ['ne','ue','ve']:
				if word not in settings['NEQUE']:
					confirm = Confirm_Sep(word)
					if confirm == 'T':
						newwords.append(word[:-2])
						newwords.append('='+word[-2:])
					else:
						settings['NEQUE'].append(word)
						newwords.append(word)
				else:
					newwords.append(word)
			elif word[-3:] in ['que']:
				if word not in settings['NEQUE']:
					if confirm == 'T':
						newwords.append(word[:-3])
						newwords.append('='+word[-3:])
					else:
						settings['NEQUE'].append(word)
						newwords.append(word)
				else:
					newwords.append(word)
			else:
				newwords.append(word)
		Output_Settings(settings)
		words = newwords
		wordid = 1
		newwords = []
		for word in words:
			aword = word_obj()
			aword.ORTHO = word
			aword.META.ID = wordid
			wordid = wordid + 1
			newwords.append(aword)
		words = newwords
		newwords = []
		for i in range(len(words)):
			cur.execute('SELECT form, morph_code, lemma_text, lemma_short_def FROM lat_parse WHERE form = "%s"' % words[i].ORTHO.lower())
			results = cur.fetchall()
			if results == ():
				Create_Lemmas(words[i].ORTHO,cur)
				cur.execute('SELECT form, morph_code, lemma_text, lemma_short_def FROM lat_parse WHERE form = "%s"' % words[i].ORTHO.lower())
				results = cur.fetchall()
			if len(results) > 1:
				lemmas = {}
				for j in range(len(results)):
					if results[j]['lemma_text'] not in lemmas.keys():
						lemmas[results[j]['lemma_text']] = {}
						lemmas[results[j]['lemma_text']]['def'] = results[j]['lemma_short_def']
						lemmas[results[j]['lemma_text']]['morphs'] = []
					if results[j]['morph_code'] not in lemmas[results[j]['lemma_text']]['morphs']:
						lemmas[results[j]['lemma_text']]['morphs'].append(results[j]['morph_code'])
				if len(lemmas.keys()) == 1:
					lemma = lemmas.keys()[0]
				else:
					lemma = Choose_Lemma(lemmas, words, i)
				if len(lemmas[lemma]['morphs']) == 1:
					morph = lemmas[lemma]['morphs'][0]
				else:
					morph = Choose_Morph(lemmas[lemma]['morphs'], words, i)
			else:
				morph = results[0]['morph_code']
				lemma = results[0]['lemma_text']
			#Here is the code the creates the correct syntactic dependencies
			newwords.append(Syntactic_Dependencies(morph, lemma, words, i))
		output = Syntax_Parse(newwords,idname,metadata,idnum)
		idnum = output[1]
		try:
			synparse[0].append(output[0][0])
		except:
			pass
	synparse.append(idnum)
	return synparse

cur = Get_Parses()
for arg in sys.argv:
	if arg[-3:] == 'txt':
		idnum = 1
		infile = open(arg)
		lines = infile.readlines()
		infile.close()
		outfile = open(arg[:-3] + 'psd','w')
		letters = []
		for line in lines:
			if line.split(':')[0] == 'ID':
				idname = line.split(':')[1]
			elif line.split(':')[0] == 'METADATA':
				metadata = Tree.parse(line.split(':')[1])
			elif line.split(':')[0] == 'TEXT':
				parseout = Parse_Letter(cur,line.split(':')[1].split(' '),idname,metadata,idnum)
				letters.append(parseout[0])
				idnum = parseout[1]
		for letter in letters:
			for token in letter:
				outfile.write(str(token))
				outfile.write('\n\n')
		outfile.close()
