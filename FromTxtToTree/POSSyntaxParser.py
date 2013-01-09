from buzhug import Base
from functools import partial
import string
from nltk.tree import *
import sys
import re
from Tkinter import *
import tkMessageBox
import tkFileDialog
import ttk
import Tkinter
import pickle

class Namespace(object):
    pass

class dt_trace(object):
    def __init__(self):
        self.form = ''
        self.head = -1
        self.relation = ''

class dt_gap(object):
    def __init__(self):
        self.gapped = ''
        self.coindex = -1

class dt_meta(object):
    def __init__(self, id):
        self.lemma = ''
        self.id = id
        self.relation = ''
        self.head = ''
        self.flags = {}

class dt_Word(object):
    def __init__(self, ortho, id):
        self.ortho = ortho
        self.pos = ''
        self.meta = dt_meta(id)
        self.trace = dt_trace()
        self.gap = dt_gap()

class meta(object):
    def __init__(self, id):
        self.lemma = Tkinter.StringVar()
        self.id = id
        self.relation = Tkinter.StringVar()
        self.head = -1
        self.flags = {}

class traces(object):
    def __init__(self):
        self.form = Tkinter.StringVar()
        self.head = -1
        self.relation = Tkinter.StringVar()

class gapping(object):
    def __init__(self):
        self.gapped = Tkinter.StringVar()
        self.coindex = -1

class Word(object):
    def __init__(self, ortho, id):
        self.ortho = ortho
        self.pos = Tkinter.StringVar()
        self.meta = meta(id)
        self.trace = traces()
        self.gap = gapping()
    
class Text(object):
    def __init__(self, meta, text, idname):
        self.meta = meta
        self.text = []
        for i in range(len(text.lstrip().split(' '))):
            self.text.append(Word(text.lstrip().split(' ')[i],i+1))
        self.display_text = ''
        for word in self.text:
            self.display_text = self.display_text + ' ' + word.ortho
        self.display_text.lstrip(' ')
        self.idname = idname
        self.checked = 0

class Environment(object):
    def __init__(self):
        self.text = Text('','','')
        self.texts = []
        self.settings = ''
        self.ignores = ''
        self.word_db = ''

def find_dependencies(text, head):
    deps = []
    for word in text:
        if word.meta.head == head.meta.id:
            deps.append(word)
    return deps

def find_token_content(text, token_heads):
    def find_dependencies(text, head):
        deps = []
        for word in text.text:
            if word.meta.head == head.meta.id:
                a_list = find_dependencies(text, word)
                if a_list == []:
                    deps.append(word)
                else:
                    deps.append(word)
                    for dep in a_list:
                        deps.append(dep)
        return deps
    tokens = []
    for head in token_heads:
        tokens.append((head,find_dependencies(text,head)))
    return tokens

def linearize(word_list):
    word_dict = {}
    for word in word_list:
        word_dict[word.meta.id] = word
    new_list = []
    for id in sorted(word_dict.keys()):
        new_list.append(word_dict[id])
    return new_list

def word_tree(word,pos):
    def get_pos(word,pos):
        output = pos[1][word.pos[0]]
        if word.meta.lemma in pos[0].keys():
            if word.pos[0] in pos[0][word.meta.lemma].keys():
                output = pos[0][word.meta.lemma][word.pos[0]]
        return output
    def update_meta(word,pos):
        output = []
        code = word.pos
        for i in range(len(code)):
            if code[i] != '-':
                output.append(Tree(str(pos[2][i][0]).upper(),[str(pos[2][i][1][code[i]])]))
        return output
    return Tree(get_pos(word,pos), [Tree('ORTHO', [word.ortho]),Tree('META', [Tree('ID', [word.meta.id]), Tree('HEAD', [word.meta.head]), Tree('RELATION', [word.meta.relation]), Tree('MORPH_CODE', [word.pos])]+update_meta(word,pos))])


def treeify(token, head, pos, index):
    def standard_dependencies(new_deps,head,output,index,pos,traces):
        rel = {'WPRO':'WNP','WADV':'WADVP','WQ':'WQP'}
        b_deps = []
        a_deps = []
        #Linearize the dependencies before and after the head
        for dep in new_deps:
            if sorted(dep.ids)[-1] < head.meta.id:
                for i in range(len(b_deps)):
                    if sorted(dep.ids)[-1] < sorted(b_deps[i].ids)[0]:
                        b_deps.insert(i,dep)
                        break
                else:
                    b_deps.append(dep)
            else:
                for i in range(len(a_deps)):
                    if sorted(dep.ids)[-1] < sorted(a_deps[i].ids)[0]:
                        a_deps.insert(i,dep)
                        break
                else:
                    a_deps.append(dep)
        #Create the tree and apply the post head dependencies
        output.tree = Tree(head.meta.relation, [word_tree(head,pos)])
        indexed = 0
        if (output.tree[0].node[0] == 'W') and (output.tree.node[0] != 'W'):
            output.tree = Tree(head.meta.relation,[Tree(rel[word_tree(head,pos).node],[word_tree(head,pos)])])
            if hasattr(head.trace,'index'):
                output.tree[0].insert(0,Tree('META',[Tree('INDEX',[head.trace.index])]))
                indexed = 1
        broken = 0
        for i in range(len(a_deps)):
            dep = a_deps[i]
            if i == 0:
                if sorted(dep.ids)[0] == head.meta.id + 1:
                    output.tree.append(dep.tree)
                    for id in dep.ids:
                        output.ids.append(id)
                else:
                    broken = 1
                    output.tree.append(Tree(dep.tree.node, [Tree('META',[Tree('ALT-ORTHO', ['*ICH*']),Tree('INDEX',[index])])]))
                    dep.tree.node = dep.tree.node.split('-')[0]
                    dep.tree.insert(0,Tree('META',[Tree('INDEX',[index])]))
                    output.ICH.append(dep)
                    index = index + 1
            elif broken == 0:
                if sorted(dep.ids)[0] == sorted(a_deps[i-1].ids)[-1] + 1:
                    output.tree.append(dep.tree)
                    for id in dep.ids:
                        output.ids.append(id)
                else:
                    broken = 1
                    output.tree.append(Tree(dep.tree.node, [Tree('META',[Tree('ALT-ORTHO', ['*ICH*']),Tree('INDEX',[index])])]))
                    dep.tree.node = dep.tree.node.split('-')[0]
                    dep.tree.insert(0,Tree('META',[Tree('INDEX',[index])]))
                    output.ICH.append(dep)
                    index = index + 1
            else:
                output.tree.append(Tree(dep.tree.node, [Tree('META',[Tree('ALT-ORTHO', ['*ICH*']),Tree('INDEX',[index])])]))
                dep.tree.node = dep.tree.node.split('-')[0]
                dep.tree.insert(0,Tree('META',[Tree('INDEX',[index])]))
                output.ICH.append(dep)
                index = index + 1
        #Now the pre head dependencies
        broken = 0
        for i in range(len(b_deps)-1,-1,-1):
            dep = b_deps[i]
            if i == len(b_deps)-1:
                if sorted(dep.ids)[-1] == head.meta.id - 1:
                    output.tree.insert(0,dep.tree)
                    for id in dep.ids:
                        output.ids.append(id)
                else:
                    broken = 1
                    output.tree.insert(0,Tree(dep.tree.node, [Tree('META',[Tree('ALT-ORTHO', ['*ICH*']),Tree('INDEX',[index])])]))
                    dep.tree.node = dep.tree.node.split('-')[0]
                    dep.tree.insert(0,Tree('META',[Tree('INDEX',[index])]))
                    output.ICH.append(dep)
                    index = index + 1
            elif broken == 0:
                if sorted(dep.ids)[-1] == sorted(b_deps[i+1].ids)[0] - 1:
                    output.tree.insert(0,dep.tree)
                    for id in dep.ids:
                        output.ids.append(id)
                else:
                    broken = 1
                    output.tree.insert(0,Tree(dep.tree.node, [Tree('META',[Tree('ALT-ORTHO', ['*ICH*']),Tree('INDEX',[index])])]))
                    dep.tree.node = dep.tree.node.split('-')[0]
                    dep.tree.insert(0,Tree('META',[Tree('INDEX',[index])]))
                    output.ICH.append(dep)
                    index = index + 1
            else:
                output.tree.insert(0,Tree(dep.tree.node, [Tree('META',[Tree('ALT-ORTHO', ['*ICH*']),Tree('INDEX',[index])])]))
                dep.tree.node = dep.tree.node.split('-')[0]
                dep.tree.insert(0,Tree('META',[Tree('INDEX',[index])]))
                output.ICH.append(dep)
                index = index + 1
        #Add in traces
        for trace in traces:
            output.tree.insert(0,trace)
        if (indexed == 0) and (hasattr(head.trace,'index')):
            output.tree.insert(0,Tree('META',[Tree('INDEX',[head.trace.index])]))
        return output, index
    class output(object):
        def __init__(self,word):
            self.tree = Tree('',[])
            self.ICH = []
            self.ids = [word.meta.id]
            self.conj = 0
            self.cp = 0
            if (head.meta.relation.split('-')[0] == 'CP') and (word_tree(head,pos).node != 'C'):
                self.cp = 1
    deps = linearize(find_dependencies(token,head))
    output = output(head)
    for dep in deps:
        if dep.meta.relation == 'CONJP':
            output.conj = 1
    new_deps = []
    for dep in deps:
        result = treeify(token,dep,pos,index)
        index = result[1]
        new_deps.append(result[0])
    for dep in new_deps:
        for ICH in dep.ICH:
            if head.meta.relation.split('-')[0] in ['IP','CP','CONJP']:
                new_deps.append(ICH)
            else:
                output.ICH.append(ICH)
        dep.ICH = []
    traces = []
    for word in token:
        if word.trace.head == head.meta.id:
            traces.append(Tree(word.trace.relation, [Tree('META',[Tree('ALT-ORTHO',[word.trace.form]),Tree('INDEX',[word.trace.index])])]))
    if head.meta.relation == 'NULL':
        output.tree = word_tree(head,pos)
    else:
        results = standard_dependencies(new_deps,head,output,index,pos,traces)
        output = results[0]
        index = results[1]
        if output.cp == 1:
            for i in range(len(output.tree)):
                if output.tree[i].node[0] == 'W':
                    output.tree.insert(i+1,Tree('C',[Tree('ALT-ORTHO',['0'])]))
                    break 
            else:
                new_node = output.tree.node
                output.tree.node = 'IP-SUB'
                output.tree = Tree(new_node,[Tree('C',[Tree('ALT-ORTHO',['0'])]),output.tree])
        try:
            if output.tree.node.split('-')[1] == 'FRL':
                new_node = 'NP-' + '-'.join(output.tree.node.split('-')[2:])
                output.tree.node = 'CP-FRL'
                for flag in head.meta.flags.keys():
                    if head.meta.flags[flag] == '1':
                        output.tree.node = output.tree.node + flag
                        if flag == '-SPE':
                            for child in output.tree:
                                if child.node.split('-')[0] in ['IP','CP']:
                                    child.node = child.node + '-SPE'
                output.tree = Tree(new_node,[output.tree])
                if head.gap.gapped == '1':
                    output.tree.node = output.tree.node + '-GAP'
                if hasattr(head.gap,'index'):
                    output.tree.insert(0,Tree('META',[Tree('INDEX',[head.gap.index])]))
                
            else:
                for flag in head.meta.flags.keys():
                    if head.meta.flags[flag] == '1':
                        output.tree.node = output.tree.node + flag
                        if flag == '-SPE':
                            for child in output.tree:
                                if child.node.split('-')[0] in ['IP','CP']:
                                    child.node = child.node + '-SPE'
                if head.gap.gapped == '1':
                    output.tree.node = output.tree.node + '-GAP'
                if hasattr(head.gap,'index'):
                    output.tree.insert(0,Tree('META',[Tree('INDEX',[head.gap.index])]))
        except:
            for flag in head.meta.flags.keys():
                if head.meta.flags[flag] == '1':
                    output.tree.node = output.tree.node + flag
                    if flag == '-SPE':
                        for child in output.tree:
                            if child.node.split('-')[0] in ['IP','CP']:
                                child.node = child.node + '-SPE'
            if head.gap.gapped == '1':
                output.tree.node = output.tree.node + '-GAP'
            if hasattr(head.gap,'index'):
                output.tree.insert(0,Tree('META',[Tree('INDEX',[head.gap.index])]))
        if output.conj == 1:
            old_node = output.tree.node
            new_tree = Tree(output.tree.node.split('-')[0],[])
            if new_tree.node in ['CP','IP']:
                new_tree.node = output.tree.node
            for i in range(len(output.tree)):
                if output.tree[i].node != 'CONJP':
                    new_tree.append(output.tree[i])
                else:
                    conj = output.tree[i]
            output.tree = Tree(old_node, [new_tree,conj])
    return output, index
    
def apply_indices(token,head,index):
    new_tok = []
    token.append(head)
    for word in token:
        hnum = 0
        if word == head:
            hnum = 1
        if word.trace.head != -1:
            word.trace.index = index
            index = index + 1
        if word.gap.gapped == '1':
            word.gap.index = index
            for word2 in token:
                if word2.meta.id == word.gap.coindex:
                    word2.gap.index = index
            index = index + 1
        if hnum == 0:
            new_tok.append(word)
        else:
            new_head = word
    return new_tok, new_head, index

def build_tree(text, psdfile,pos):
    text = deTkinter([text])[0]
    token_heads = []
    for word in text.text:
        print word.meta.id
        if word.meta.head == 0:
            token_heads.append(word)
    tokens = find_token_content(text,token_heads)
    trees = []
    idnum = 1
    for token in tokens:
        id_tree = Tree('ID',[text.idname + '.' + str(idnum)])
        idnum = idnum + 1
        result = apply_indices(token[1],token[0],1)
        result[0].append(result[1])        
        text_tree = treeify(result[0],result[1], pos, result[2])[0].tree
        trees.append(Tree('',[text.meta,text_tree,id_tree]))
    for tree in trees:
        print str(tree)
        psdfile.write(str(tree) + '\n' + '\fn')
    

def deTkinter(texts):
    new_texts = []
    for text in texts:
        a_text = Namespace()
        a_text.meta = text.meta
        a_text.idname = text.idname
        a_text.checked = text.checked
        a_text.text = []
        for word in text.text:
            a_word = dt_Word(word.ortho, word.meta.id)
            a_word.pos = word.pos.get()
            a_word.meta.lemma = word.meta.lemma.get()
            a_word.meta.relation = word.meta.relation.get()
            a_word.meta.head = word.meta.head
            for flag in word.meta.flags.keys():
                a_word.meta.flags[flag] = word.meta.flags[flag].get()
            a_word.trace.head = word.trace.head
            a_word.trace.form = word.trace.form.get()
            a_word.trace.relation = word.trace.relation.get()
            a_word.gap.coindex = word.gap.coindex
            a_word.gap.gapped = word.gap.gapped.get()
            a_text.text.append(a_word)
        new_texts.append(a_text)
    return new_texts

def reTkinter(texts):
    new_texts = []
    for text in texts:
        a_text = Text(text.meta,'',text.idname)
        a_text.checked = text.checked
        a_text.text = []
        for word in text.text:
            a_word = Word(word.ortho, word.meta.id)
            a_word.pos.set(word.pos)
            a_word.meta.lemma.set(word.meta.lemma)
            a_word.meta.relation.set(word.meta.relation)
            a_word.meta.head = word.meta.head
            for flag in word.meta.flags.keys():
                a_word.meta.flags[flag] = Tkinter.StringVar()
                a_word.meta.flags[flag].set(word.meta.flags[flag])
            a_word.trace.head = word.trace.head
            a_word.trace.form.set(word.trace.form)
            a_word.trace.relation.set(word.trace.relation)
            a_word.gap.coindex = word.gap.coindex
            a_word.gap.gapped.set(word.gap.gapped)
            a_text.text.append(a_word)
        new_texts.append(a_text)
    return new_texts

def read_text(txtfile):
    texts = []
    idname = ''
    meta = ''
    text = ''
    for line in txtfile:
        if line.split(':')[0] == 'ID':
            idname = line.split(':')[1].rstrip()
        elif line.split(':')[0] == 'METADATA':
            meta = Tree.parse(line.split(':')[1].rstrip())
        elif line.split(':')[0] == 'TEXT':
            text = line.split(':')[1]
            newtext = ''
            for word in text.split():
                try:
                    punctuation = (',','.','"',"'",'?','!','(',')')
                    newwords = [word]
                    if newwords[0][-1] in punctuation:
                        newwords = [newwords[0][:-1],newwords[0][-1]]
                        if newwords[0][-1] in punctuation:
                            newwords = [newwords[0][:-1],newwords[0][-1],newwords[-1]]
                    if newwords[0][0] in punctuation:
                        cur_word = newwords[0]
                        newwords[0] = cur_word[1:]
                        newwords.insert(0,cur_word[0])
                    for cur_word in newwords:
                        newtext = newtext + ' ' + cur_word
                except:
                    pass
            text = newtext
            newtext = Text(meta,text,idname)
            texts.append(newtext)
    return texts
    
def read_settings(setfile):
    settings = {}
    for line in setfile:
        settings[line.split(':')[0]] = line.split(':')[1].rstrip()
    db = Base(settings['db']).open()
    if 'sep_suffix' in settings.keys():
        settings['sep_suffix'] = settings['sep_suffix'].split(',')
    if 'pos_codes' in settings.keys():
            pos_codes = settings['pos_codes'].split(';')
            settings['new_pos_codes'] = []
            for pos_code in pos_codes:
                settings['new_pos_codes'].append([pos_code.split('.')[0],{}])
                for values in pos_code.split('.')[1].split(','):
                    settings['new_pos_codes'][-1][1][values.split('=')[0]]=values.split('=')[1]
    if 'syn_rel' in settings.keys():
        list = settings['syn_rel'].split(';')
        settings['new_syn_rel'] = {}
        for form in list:
            newform = r''
            for char in form.split('=')[0]:
                if char == '-':
                    newform = newform + r'.'
                else:
                    newform = newform + char
            settings['new_syn_rel'][newform]=form.split('=')[1].split(',')
    if 'empty_cat' in settings.keys():
        list = settings['empty_cat'].split(';')
        settings['new_empty'] = {}
        for form in list:
            newform = r''
            for char in form.split('=')[0]:
                if char == '-':
                    newform = newform + r'.'
                else:
                    newform = newform + char
            settings['new_empty'][newform]=[form.split('=')[1]]+[form.split('=')[2].split(',')]
    if 'flags' in settings.keys():
        settings['new_flags'] = settings['flags'].split(',')
    if 'pos_lemma' in settings.keys():
        settings['new_pos_lemma'] = {}
        for lemma in settings['pos_lemma'].split('\t'):
            form = lemma.split(';')[0]
            settings['new_pos_lemma']['form'] = {}
            for parse in lemma.split(';')[1].split(','):
                settings['new_pos_lemma']['form'][parse.split('=')[0]] = parse.split('=')[1]
    if 'pos_output' in settings.keys():
        settings['new_pos_output'] = {}
        for parse in settings['pos_output'].split('\t'):
            settings['new_pos_output'][parse.split('=')[0]] = parse.split('=')[1]
    if 'relative_clause' in settings.keys():
        settings['new_relative_clause'] = settings['relative_clause'].split(',')
    return settings['sep_suffix'], db, settings['new_pos_codes'],settings['new_syn_rel'],settings['new_empty'],settings['new_flags'],settings['new_pos_lemma'],settings['new_pos_output'],settings['new_relative_clause']

def read_ignore(ignfile):
    ignore = Namespace()
    ignore.split = []
    ignore.keep = []
    for line in ignfile:
        if line.split(':')[0] == 'SPLIT':
            newline = line.split(':')[1]
            newline = newline.split(',')
            for word in newline:
                ignore.split.append(word.rstrip())
        elif line.split(':')[0] == 'KEEP':
            for word in line.split(':')[1].split(','):
                ignore.keep.append(word.rstrip())
    return ignore


def create_root():
    root = Tk()
    root.title('POS/Syntax Parser')
    root.option_add('*tearOff', FALSE)
    
    root.columnconfigure(0,weight=1)
    root.rowconfigure(0,weight=1)
    root.rowconfigure(1,weight=1)
    root.rowconfigure(2,weight=1)

    def find_traces(*args):
        for widget in environ.empty_options:
            widget.destroy()
        for widget in environ.empty_relations:
            widget.destroy()
        environ.empty_options = []
        environ.empty_options_text = []
        environ.empty_relations = []
        environ.empty_relations_text = []
        for key in environ.empty.keys():
            match = re.search(key,args[0])
            if match:
                environ.empty_options_text = [''] + [environ.empty[key][0]]
                environ.empty_relations_text = [''] + environ.empty[key][1]
                break
            else:
                continue
        for i in range(len(environ.empty_options_text)):
            environ.empty_options.append(ttk.Radiobutton(empty_frame, text=environ.empty_options_text[i], variable=environ.texts[environ.text_sel].text[environ.cur_sel.value].trace.form, value=environ.empty_options_text[i]))
            environ.empty_options[-1].grid(column = 0, row = (3 + i), sticky=(W,E))
        for i in range(len(environ.empty_relations_text)):
            environ.empty_relations.append(ttk.Radiobutton(empty_frame, text=environ.empty_relations_text[i], variable=environ.texts[environ.text_sel].text[environ.cur_sel.value].trace.relation, value=environ.empty_relations_text[i]))
            environ.empty_relations[-1].grid(column = 1, row = (3 + i), sticky=(W,E))
        if ('*T*' in environ.empty_options_text) and (environ.texts[environ.text_sel].text[environ.cur_sel.value].meta.relation[0] == 'W'):
            environ.texts[environ.text_sel].text[environ.cur_sel.value].trace.form.set('*T*')
            environ.texts[environ.text_sel].text[environ.cur_sel.value].trace.relation.set(environ.empty_relations_text[1])
        
    def find_relations(*args):
        for widget in environ.rel_options:
            widget.destroy()
        environ.rel_options = []
        environ.rel_options_text = []
        for key in environ.syn_rel.keys():
            match = re.search(key,args[0])
            if match:
                environ.rel_options_text = environ.syn_rel[key]
                break
            else:
                continue
        for i in range(len(environ.rel_options_text)):
            environ.rel_options.append(ttk.Radiobutton(syntax_frame, text=environ.rel_options_text[i], variable=environ.texts[environ.text_sel].text[environ.cur_sel.value].meta.relation, value=environ.rel_options_text[i]))
            environ.rel_options[-1].grid(column = 0, row = (3 + i), sticky=(W,E))
        if len(environ.rel_options) > 0:
            if environ.texts[environ.text_sel].text[environ.cur_sel.value].meta.relation.get() == '':
                environ.texts[environ.text_sel].text[environ.cur_sel.value].meta.relation.set(environ.rel_options[0]['text'])
            find_traces(environ.texts[environ.text_sel].text[environ.cur_sel.value].pos.get())
    
    def find_pos(*args):
        def run_both(*args):
            find_relations(environ.texts[environ.text_sel].text[environ.cur_sel.value].pos.get())
            find_traces(environ.texts[environ.text_sel].text[environ.cur_sel.value].pos.get())
        def full_pos(*args):
            text = ''
            pos = args[0]
            for i in range(len(pos)):
                if pos[i] != '-':
                    text = text + str(environ.pos_codes[i][0]) +': ' + str(environ.pos_codes[i][1][pos[i]]) + '\n'
            return text
        for widget in environ.pos_options:
            widget.destroy()
        environ.pos_options = []
        environ.pos_options_text = []
        for i in range(len(environ.texts[environ.text_sel].text[environ.cur_sel.value].lookup)):
            cur_lemma = environ.texts[environ.text_sel].text[environ.cur_sel.value].lookup[i].lemma_text
            cur_lnum = environ.texts[environ.text_sel].text[environ.cur_sel.value].lookup[i].lemma_num
            lemma = args[0].rstrip('0123456789')
            lnum = args[0].lstrip(string.letters + string.punctuation + string.punctuation)
            if lnum == '':
                lnum = '1'
            pos = environ.texts[environ.text_sel].text[environ.cur_sel.value].lookup[i].morph_code
            if cur_lemma == lemma:
                if cur_lnum == lnum:
                    if pos not in environ.pos_options_text:
                        environ.pos_options_text.append(pos)
                        environ.pos_options.append(ttk.Radiobutton(pos_frame, text=pos, variable=environ.texts[environ.text_sel].text[environ.cur_sel.value].pos, value=pos, command=run_both))
                        environ.pos_options[-1].grid(column=0,row=len(environ.pos_options),sticky=(W,E))    
                        text = full_pos(pos)
                        environ.pos_options[-1].bind('<Enter>',lambda e,text=text: set_help_value(str(text)))
        if len(environ.pos_options) > 0:
            if environ.texts[environ.text_sel].text[environ.cur_sel.value].pos.get() == '':
                environ.texts[environ.text_sel].text[environ.cur_sel.value].pos.set(environ.pos_options[0]['text'])
            find_relations(environ.texts[environ.text_sel].text[environ.cur_sel.value].pos.get())
        else:
            for widget in environ.rel_options:
                widget.destroy()
            for widget in environ.empty_options:
                widget.destroy()
            for widget in environ.empty_relations:
                widget.destroy()

    def find_lemmas():
        for widget in environ.lemma_options:
            widget.destroy()
        environ.lemma_options = []
        environ.lemma_options_text = []
        for i in range(len(environ.texts[environ.text_sel].text[environ.cur_sel.value].lookup)):
            lemma = environ.texts[environ.text_sel].text[environ.cur_sel.value].lookup[i].lemma_text
            if environ.texts[environ.text_sel].text[environ.cur_sel.value].lookup[i].lemma_num != '1':
                lemma = lemma + environ.texts[environ.text_sel].text[environ.cur_sel.value].lookup[i].lemma_num
            if lemma not in environ.lemma_options_text:
                environ.lemma_options_text.append(lemma)
                environ.lemma_options.append(ttk.Radiobutton(lemma_frame, text=lemma, variable=environ.texts[environ.text_sel].text[environ.cur_sel.value].meta.lemma, value=lemma, command = lambda e = lemma: find_pos(e)))
                environ.lemma_options[-1].grid(column=0,row=len(environ.lemma_options),sticky=(W,E))    
                text = 'Definition: ' + str(environ.texts[environ.text_sel].text[environ.cur_sel.value].lookup[i].lemma_short_def)
                environ.lemma_options[-1].bind('<Enter>',lambda e, text = text: set_help_value(text))
        if len(environ.lemma_options) > 0:
            if environ.texts[environ.text_sel].text[environ.cur_sel.value].meta.lemma.get() == '':
                environ.texts[environ.text_sel].text[environ.cur_sel.value].meta.lemma.set(environ.lemma_options[0]['text'])
            find_pos(environ.texts[environ.text_sel].text[environ.cur_sel.value].meta.lemma.get())
        else:
            for widget in environ.pos_options:
                widget.destroy()
            for widget in environ.rel_options:
                widget.destroy()
            for widget in environ.empty_options:
                widget.destroy()
            for widget in environ.empty_relations:
                widget.destroy()
    
    def create_flags():
        for widget in environ.flag_boxes:
            widget.destroy()
        for i in range(len(environ.flags)):
            flag = environ.flags[i]
            try:
                environ.flag_boxes.append(Tkinter.Checkbutton(syntax_frame, text=flag, variable = environ.texts[environ.text_sel].text[environ.cur_sel.value].meta.flags[flag]))
                environ.flag_boxes[-1].grid(column=1,row=(3 + i))
            except:
                environ.texts[environ.text_sel].text[environ.cur_sel.value].meta.flags[flag] = Tkinter.StringVar()
                environ.texts[environ.text_sel].text[environ.cur_sel.value].meta.flags[flag].set('0')
                environ.flag_boxes.append(Tkinter.Checkbutton(syntax_frame, text=flag, variable = environ.texts[environ.text_sel].text[environ.cur_sel.value].meta.flags[flag]))
                environ.flag_boxes[-1].grid(column=1,row=(3 + i))
        environ.flag_boxes.append(Tkinter.Checkbutton(gap_frame, text='Gapped?', variable = environ.texts[environ.text_sel].text[environ.cur_sel.value].gap.gapped))
        environ.flag_boxes[-1].grid(column=0,row=2)
        
    def push_buttons(i):
        word_num = 11
        if len(environ.texts[environ.text_sel].text) < word_num:
            word_num = len(environ.texts[environ.text_sel].text)-1
        if environ.work_option.get() == 'cur_word':
            if scalevalue.get() < 5:
                environ.cur_sel.value = i
            elif scalevalue.get() > len(environ.texts[environ.text_sel].text)-6:
                environ.cur_sel.value = len(environ.texts[environ.text_sel].text)-(word_num)+i
            else:
                environ.cur_sel.value = scalevalue.get()-5+i
            try:
                environ.cur_word_text.set(environ.texts[environ.text_sel].text[environ.cur_sel.value].ortho)
                try:
                    if environ.texts[environ.text_sel].text[environ.cur_sel.value].meta.head == 0:
                        environ.head_word_text.set('Token')
                    else:
                        for word in environ.texts[environ.text_sel].text:
                            if word.meta.id == environ.texts[environ.text_sel].text[environ.cur_sel.value].gap.coindex:
                                environ.gap_word_text.set(word.ortho)
                                break
                        else:
                            environ.gap_word_text.set('')
                        for word in environ.texts[environ.text_sel].text:
                            if word.meta.id == environ.texts[environ.text_sel].text[environ.cur_sel.value].trace.head:
                                environ.empty_word_text.set(word.ortho)
                                break
                        else:
                            environ.empty_word_text.set('')
                        for word in environ.texts[environ.text_sel].text:
                            if word.meta.id == environ.texts[environ.text_sel].text[environ.cur_sel.value].meta.head:
                                environ.head_word_text.set(word.ortho)
                                break
                        else:
                            environ.head_word_text.set('')
                except:
                        environ.head_word_text.set('')
                create_flags()
                set_buttons()
                environ.texts[environ.text_sel].text[environ.cur_sel.value].lookup = environ.word_db.select(form = environ.texts[environ.text_sel].text[environ.cur_sel.value].ortho.lower())
                find_lemmas()
            except:
                pass
        elif environ.work_option.get() == 'trace_head':
            if scalevalue.get() < 5:
                environ.texts[environ.text_sel].text[environ.cur_sel.value].trace.head = environ.texts[environ.text_sel].text[i].meta.id
            elif scalevalue.get() > len(environ.texts[environ.text_sel].text)-6:
                environ.texts[environ.text_sel].text[environ.cur_sel.value].trace.head = environ.texts[environ.text_sel].text[len(environ.texts[environ.text_sel].text)-(word_num)+i].meta.id
            else:
                environ.texts[environ.text_sel].text[environ.cur_sel.value].trace.head = environ.texts[environ.text_sel].text[scalevalue.get()-5+i].meta.id
            try:
                for word in environ.texts[environ.text_sel].text:
                    if word.meta.id == environ.texts[environ.text_sel].text[environ.cur_sel.value].trace.head:
                        environ.empty_word_text.set(word.ortho)
            except:
                environ.head_word_text.set('')
        elif environ.work_option.get() == 'gap_head':
            if scalevalue.get() < 5:
                environ.texts[environ.text_sel].text[environ.cur_sel.value].gap.coindex = environ.texts[environ.text_sel].text[i].meta.id
            elif scalevalue.get() > len(environ.texts[environ.text_sel].text)-6:
                environ.texts[environ.text_sel].text[environ.cur_sel.value].gap.coindex = environ.texts[environ.text_sel].text[len(environ.texts[environ.text_sel].text)-(word_num)+i].meta.id
            else:
                environ.texts[environ.text_sel].text[environ.cur_sel.value].gap.coindex = environ.texts[environ.text_sel].text[scalevalue.get()-5+i].meta.id
            try:
                for word in environ.texts[environ.text_sel].text:
                    if word.meta.id == environ.texts[environ.text_sel].text[environ.cur_sel.value].gap.coindex:
                        environ.gap_word_text.set(word.ortho)
            except:
                environ.head_word_text.set('')
        else:
            if scalevalue.get() < 5:
                environ.texts[environ.text_sel].text[environ.cur_sel.value].meta.head = environ.texts[environ.text_sel].text[i].meta.id
            elif scalevalue.get() > len(environ.texts[environ.text_sel].text)-6:
                environ.texts[environ.text_sel].text[environ.cur_sel.value].meta.head = environ.texts[environ.text_sel].text[len(environ.texts[environ.text_sel].text)-(word_num)+i].meta.id
            else:
                environ.texts[environ.text_sel].text[environ.cur_sel.value].meta.head = environ.texts[environ.text_sel].text[scalevalue.get()-5+i].meta.id
            try:
                for word in environ.texts[environ.text_sel].text:
                    if word.meta.id == environ.texts[environ.text_sel].text[environ.cur_sel.value].meta.head:
                        environ.head_word_text.set(word.ortho)
            except:
                environ.head_word_text.set('')
    def set_buttons(*args):
        wordforwardbutton.configure(state=NORMAL)
        wordbackbutton.configure(state=NORMAL)
        if environ.cur_sel.value == len(environ.texts[environ.text_sel].text)-1:
            wordforwardbutton.configure(state=DISABLED)
        if environ.cur_sel.value == 0:
            wordbackbutton.configure(state=DISABLED)
        def Set_Display_Text():
            try:
                environ.texts[environ.text_sel].display_text = ''
                for i in range(len(environ.texts[environ.text_sel].text)):
                    if i == environ.cur_sel.value:
                        environ.texts[environ.text_sel].display_text = environ.texts[environ.text_sel].display_text + ' ' + environ.texts[environ.text_sel].text[i].ortho.upper()
                    else:
                        environ.texts[environ.text_sel].display_text = environ.texts[environ.text_sel].display_text + ' ' + environ.texts[environ.text_sel].text[i].ortho
                maintext['state'] = 'normal'
                maintext.delete('1.0',END)
                maintext.insert('1.0',environ.texts[environ.text_sel].display_text)
                maintext['state'] = 'disabled'
            except:
                pass
        word_num = 11
        if len(environ.texts[environ.text_sel].text) < word_num:
            word_num = len(environ.texts[environ.text_sel].text)
        for i in range(word_num):
            if (scalevalue.get() < 5) or (len(environ.texts[environ.text_sel].text)<=11):
                try:
                    topbuttontext[i].set(environ.texts[environ.text_sel].text[i].ortho)
                except:
                    topbuttontext[i].set('')
                if i == environ.cur_sel.value:
                    topbuttontext[i].set(topbuttontext[i].get().upper())                
            elif scalevalue.get() > len(environ.texts[environ.text_sel].text)-6:
                try:
                    topbuttontext[i].set(environ.texts[environ.text_sel].text[len(environ.texts[environ.text_sel].text)-(word_num)+i].ortho)
                except:
                    topbuttontext[i].set('')
                if len(environ.texts[environ.text_sel].text)-(word_num)+i == environ.cur_sel.value:
                    topbuttontext[i].set(topbuttontext[i].get().upper())                
            else:
                try:
                    topbuttontext[i].set(environ.texts[environ.text_sel].text[scalevalue.get()-5+i].ortho)
                except:
                    topbuttontext[i].set('')
                if scalevalue.get()-5+i == environ.cur_sel.value:
                    topbuttontext[i].set(topbuttontext[i].get().upper())     
        Set_Display_Text()
    environ = Environment()
    environ.cur_sel = Namespace()
    environ.cur_sel.value = 0

    environ.help_value = Tkinter.StringVar()
    environ.work_option = Tkinter.StringVar()
    
    def set_help_value(*args):
        help_text['state'] = 'normal'
        help_text.delete('1.0',END)
        help_text.insert('1.0',args[0])
        help_text['state'] = 'disabled'
    
    topframe = ttk.Frame(root,padding='5')
    topframe.grid(column=0,row=0,sticky=(W,E,N))
    for i in range(11):
        topframe.columnconfigure(i+1,weight=1)
    scalevalue = Tkinter.IntVar()
    scalelen = Tkinter.IntVar()
    scalevalue.set(0)
    
    topbuttons = []
    topbuttontext = []
    for i in range(11):
        topbuttontext.append(Tkinter.StringVar())
        topbuttons.append(Tkinter.Button(topframe,textvariable=topbuttontext[-1],command=lambda i=i: push_buttons(i)))
        topbuttons[-1].grid(column=i+1,row=0,sticky='NSWE')
    
    topscale = Tkinter.Scale(topframe,variable=scalevalue,from_=0,to=0,orient=HORIZONTAL,command = set_buttons)
    topscale.grid(column=1,row=1,columnspan=11,sticky='WE')
    
    def word_back():
        environ.cur_sel.value = environ.cur_sel.value - 1
        topscale.set(environ.cur_sel.value)
        wordforwardbutton.configure(state=NORMAL)
        wordbackbutton.configure(state=NORMAL)
        if environ.cur_sel.value == len(environ.texts[environ.text_sel].text)-1:
            wordforwardbutton.configure(state=DISABLED)
        if environ.cur_sel.value == 0:
            wordbackbutton.configure(state=DISABLED)
        try:
            environ.cur_word_text.set(environ.texts[environ.text_sel].text[environ.cur_sel.value].ortho)
            try:
                if environ.texts[environ.text_sel].text[environ.cur_sel.value].meta.head == 0:
                    environ.head_word_text.set('Token')
                else:
                    for word in environ.texts[environ.text_sel].text:
                        if word.meta.id == environ.texts[environ.text_sel].text[environ.cur_sel.value].meta.head:
                            environ.head_word_text.set(word.ortho)
                            break
                    else:
                        environ.head_word_text.set('')
            except:
                    environ.head_word_text.set('')
            create_flags()
            set_buttons()
            environ.texts[environ.text_sel].text[environ.cur_sel.value].lookup = environ.word_db.select(form = environ.texts[environ.text_sel].text[environ.cur_sel.value].ortho.lower())
            find_lemmas()
        except:
            pass
        
    def word_forward():
        environ.cur_sel.value = environ.cur_sel.value + 1
        topscale.set(environ.cur_sel.value)
        wordforwardbutton.configure(state=NORMAL)
        wordbackbutton.configure(state=NORMAL)
        if environ.cur_sel.value == len(environ.texts[environ.text_sel].text)-1:
            wordforwardbutton.configure(state=DISABLED)
        if environ.cur_sel.value == 0:
            wordbackbutton.configure(state=DISABLED)
        try:
            environ.cur_word_text.set(environ.texts[environ.text_sel].text[environ.cur_sel.value].ortho)
            try:
                if environ.texts[environ.text_sel].text[environ.cur_sel.value].meta.head == 0:
                    environ.head_word_text.set('Token')
                else:
                    for word in environ.texts[environ.text_sel].text:
                        if word.meta.id == environ.texts[environ.text_sel].text[environ.cur_sel.value].meta.head:
                            environ.head_word_text.set(word.ortho)
                            break
                    else:
                        environ.head_word_text.set('')
            except:
                    print 'error!!!'
                    environ.head_word_text.set('')
            create_flags()
            set_buttons()
            environ.texts[environ.text_sel].text[environ.cur_sel.value].lookup = environ.word_db.select(form = environ.texts[environ.text_sel].text[environ.cur_sel.value].ortho.lower())
            find_lemmas()
        except:
            pass
    
    def scale_back():
        if topscale.get() > 0:
            topscale.set(topscale.get()-1)
    def scale_for():
        if topscale.get() < topscale['to']:
            topscale.set(topscale.get()+1)
    scalebackbutton = Tkinter.Button(topframe,text='<',command=scale_back)
    scalebackbutton.grid(column=0,row=1)
    scaleforbutton = Tkinter.Button(topframe,text='>',command=scale_for)
    scaleforbutton.grid(column=13,row=1)
    
    mainframe = ttk.Frame(root,padding='5')
    mainframe.grid(column=0,row=2,sticky=(N,W,E))
    mainframe.columnconfigure(0,weight=1)
    mainframe.columnconfigure(1,weight=1)
    mainframe.columnconfigure(2,weight=1)
    mainframe.rowconfigure(0,weight=1)
    
    leftframe = ttk.Frame(mainframe)
    leftframe.grid(column=0,row=0,sticky=(N,W,E))
    leftframe.columnconfigure(0,weight=1)
    leftframe.rowconfigure(0,weight=1)
    leftframe.rowconfigure(2,weight=1)
    leftframe.rowconfigure(4,weight=1)
    leftframe.rowconfigure(6,weight=1)
    
    cur_word_frame = ttk.Frame(leftframe,padding='5')
    cur_word_frame.grid(column=0,row=0,sticky=(W,E,N))
    cur_word_frame.columnconfigure(0,weight=1)
    cur_word_frame.rowconfigure(0,weight=1)
    
    wordbackbutton = Tkinter.Button(cur_word_frame,text='<',command=word_back)
    wordbackbutton.grid(column=0,row=2)
    wordforwardbutton = Tkinter.Button(cur_word_frame,text='>',command=word_forward)
    wordforwardbutton.grid(column=1,row=2)
    
    cur_word_tag = Tkinter.Label(cur_word_frame, text='Current Word:')
    cur_word_tag.grid(column=0,row=0,sticky=(W,E,N))
    
    environ.cur_word_text = Tkinter.StringVar()
    cur_word_text = Tkinter.Label(cur_word_frame, textvariable=environ.cur_word_text)
    cur_word_text.grid(column=1,row=0,sticky=(W,E,N))
    
    cur_word_rbutton = ttk.Radiobutton(cur_word_frame, text='Set Working Word', variable=environ.work_option, value='cur_word')
    cur_word_rbutton.grid(column=0,columnspan=2,row=1)
    environ.work_option.set('cur_word')
    
    hll1=Frame(leftframe,height=1,bg="black")
    hll1.grid(column=0,row=1,sticky='WE')
    
    lemma_frame = ttk.Frame(leftframe,padding='5')
    lemma_frame.grid(column=0,row=2,sticky=(W,E))
    lemma_frame.columnconfigure(0,weight=1)
    lemma_frame.rowconfigure(0,weight=1)
    
    environ.lemma_options = []
    
    lemma_tag = Tkinter.Label(lemma_frame, text='Lemma:')
    lemma_tag.grid(column=0,row=0,sticky=(W))
    
    hll2=Frame(leftframe,height=1,bg="black")
    hll2.grid(column=0,row=3,sticky='WE')
    
    pos_frame = ttk.Frame(leftframe,padding='5')
    pos_frame.grid(column=0,row=4,sticky=(W,E))
    pos_frame.columnconfigure(0,weight=1)
    pos_frame.rowconfigure(0,weight=1)
    
    environ.pos_options = []
    
    pos_tag = Tkinter.Label(pos_frame, text='Morphology:')
    pos_tag.grid(column=0,row=0,sticky=(W))
    
    hll3=Frame(leftframe,height=1,bg="black")
    hll3.grid(column=0,row=5,sticky='WE')
    
    syntax_frame = ttk.Frame(leftframe,padding='5')
    syntax_frame.grid(column=0,row=6,sticky=(W,E,S))
    syntax_frame.columnconfigure(0,weight=1)
    syntax_frame.rowconfigure(0,weight=1)
    
    head_word_tag = Tkinter.Label(syntax_frame, text='Head Word:')
    head_word_tag.grid(column=0,row=0,sticky=(W,E,N))
    
    environ.head_word_text = Tkinter.StringVar()
    head_word_text = Tkinter.Label(syntax_frame, textvariable=environ.head_word_text)
    head_word_text.grid(column=1,row=0,sticky=(W,E,N))
    
    syntax_rbutton = ttk.Radiobutton(syntax_frame, text='Set Head Word', variable=environ.work_option, value='head_word')
    syntax_rbutton.grid(column=0,row=1)
    
    def push_head_button():
        environ.head_word_text.set('Token')
        environ.texts[environ.text_sel].text[environ.cur_sel.value].meta.head = 0
    
    head_button = ttk.Button(syntax_frame, text='Token Head', command = push_head_button)
    head_button.grid(column=1, row=1)
    
    environ.rel_options = []
    
    syn_tag = Tkinter.Label(syntax_frame, text='Syntactic Relations:')
    syn_tag.grid(column=0,row=2,sticky=(W))
    
    environ.flag_boxes = []
    
    centerframe = ttk.Frame(mainframe)
    centerframe.grid(column=1,row=0,sticky=(N,W,E))
    centerframe.columnconfigure(0,weight=1)
    centerframe.rowconfigure(0,weight=1)
    centerframe.rowconfigure(1,weight=1)
    
    maintext = Tkinter.Text(centerframe,state = 'disabled',wrap='word',width = 50,height = 10)
    maintext.grid(column=0,row=0)
    maintextscroll = Tkinter.Scrollbar(centerframe,orient=VERTICAL, command=maintext.yview)
    maintextscroll.grid(column=1,row=0,sticky='N,S,W')
    maintext.configure(yscrollcommand=maintextscroll.set)
    
    bottomframe = ttk.Frame(centerframe)
    bottomframe.grid(column=0,row=1,sticky=(N,S,W,E))
    bottomframe.columnconfigure(0,weight=1)
    bottomframe.columnconfigure(1,weight=1)
    bottomframe.columnconfigure(2,weight=1)
    bottomframe.columnconfigure(3,weight=1)
    bottomframe.rowconfigure(0,weight=1)    
    bottomframe.rowconfigure(1,weight=1)
    
    bt_text_label = Tkinter.Label(bottomframe, text='Back Text')
    bt_text_label.grid(column=0,row=0,sticky=(W))
    
    ft_text_label = Tkinter.Label(bottomframe, text='Forward Text')
    ft_text_label.grid(column=3,row=0,sticky=(E))
    
    def set_text():
        wordbackbutton.configure(state=DISABLED)
        maintext['state'] = 'normal'
        maintext.delete('1.0',END)
        maintext.insert('1.0',environ.texts[environ.text_sel].display_text)
        maintext['state'] = 'disabled'
        topscale['to'] = len(environ.texts[environ.text_sel].text)-1
        topscale.set(0)
        variable=environ.work_option.set('cur_word')
        set_buttons()
        push_buttons(0)
        variable=environ.work_option.set('head_word')
        
    def suffix_check():
        newtext = []
        suflen = 0
        needs_checking = []
        for suffix in environ.sep_suf:
            if len(suffix) > suflen:
                suflen = len(suffix)
        for word_full in environ.texts[environ.text_sel].text:
            word = word_full.ortho
            if word not in environ.ignores.keep + environ.ignores.split:
                for i in range(suflen*-1,-1,1):
                    if len(word)*-1 < i:
                        for suffix in environ.sep_suf:
                            if word[i:] == suffix:
                                needs_checking.append((word,suffix))
                                break
                        else:
                            continue
                        break
        for word_full in environ.texts[environ.text_sel].text:
            newtext.append(word_full.ortho)
        def newOutput(wordlist):
            newwords = []
            suflen = 0
            for suffix in environ.sep_suf:
                if len(suffix) > suflen:
                    suflen = len(suffix)
            for word in wordlist:
                if word in environ.ignores.split:
                    for i in range(suflen*-1,-1,1):
                        for suffix in environ.sep_suf:
                            if word[i:] == suffix:
                                newwords.append(word[:i])
                                newwords.append(word[i:])
                                break
                        else:
                            continue
                        break
                else:
                    newwords.append(word)
            newtext = ''
            for word in newwords:
                newtext = newtext + ' ' + word
            environ.texts[environ.text_sel] = Text(environ.texts[environ.text_sel].meta,newtext.lstrip(),environ.texts[environ.text_sel].idname)
            environ.texts[environ.text_sel].checked = 1
            set_text()
        topscale['to'] = len(newtext)-1        
        if len(needs_checking) > 0:
            def exit():
                for i in range(len(suffix_checkboxs)):
                    if suffix_checkboxs_vars[i].get() == '1':
                        environ.ignores.split.append(needs_checking[i][0])
                    else:
                        environ.ignores.keep.append(needs_checking[i][0])
                newOutput(newtext)
                suffix_confirm.destroy()
            suffix_confirm = Tkinter.Toplevel(root)
            suffix_confirm.protocol("WM_DELETE_WINDOW", exit)
            suffix_confirm.title = 'Confirmation'
            suffix_frame = ttk.Frame(suffix_confirm)
            suffix_frame.grid(column=0,row=0)
            suffix_checkboxs = []
            suffix_checkboxs_vars = []
            for pair in needs_checking:
                suffix_checkboxs_vars.append(Tkinter.StringVar())
                suffix_checkboxs_vars[-1].set('0')
                suffix_checkboxs.append(Tkinter.Checkbutton(suffix_frame, text = str('Does ' + pair[0] + ' have the suffix ' + pair[1] + ' on it?'),variable=suffix_checkboxs_vars[-1]))
                suffix_checkboxs[-1].grid(column=0,row=len(suffix_checkboxs)-1)
            suffix_close_button = Tkinter.Button(suffix_frame,text='Close',command=exit)
            suffix_close_button.grid(column = 0,row=len(suffix_checkboxs))
        else:
            newOutput(newtext)
                    
    def previous_text():
        environ.text_sel = environ.text_sel - 1
        if environ.texts[environ.text_sel].checked == 0:
            suffix_check()
        else:
            set_text()
        forward_text.configure(state=NORMAL)
        if environ.text_sel == 0:
            back_text.configure(state=DISABLED)
        
    
    def next_text():
        environ.text_sel = environ.text_sel + 1
        if environ.texts[environ.text_sel].checked == 0:
            suffix_check()
        else:
            set_text()
        back_text.configure(state=NORMAL)
        if environ.text_sel == len(environ.texts)-1:
            forward_text.configure(state=DISABLED)
    
    help_tag = Tkinter.Label(bottomframe, text='Information Box:')
    help_tag.grid(column=1,row=0,sticky=(W))
    
    help_text = Tkinter.Text(bottomframe,state = 'disabled',wrap='word',height = 8,width=50)
    help_text.grid(column=1,row=1)
    set_help_value("Scroll over items to display more information")

    helptextscroll = Tkinter.Scrollbar(bottomframe,orient=VERTICAL, command=help_text.yview)
    helptextscroll.grid(column=2,row=1,sticky='NSW')
    help_text.configure(yscrollcommand=helptextscroll.set)
    
    help_box = Tkinter.Label(bottomframe, textvariable=environ.help_value)
    help_box.grid(column=1,row=1,sticky=(W))
    
    back_text = Tkinter.Button(bottomframe,text='<',command=previous_text)
    back_text.bind('<Enter>',lambda e: set_help_value('Go back one text in set of project texts.'))
    back_text.grid(column=0,row=1,sticky=(W))
    back_text.configure(state=DISABLED)
    
    forward_text = Tkinter.Button(bottomframe,text='>',command=next_text)
    forward_text.grid(column=3,row=1,sticky=(E))    
    forward_text.bind('<Enter>',lambda e: set_help_value('Go forward one text in set of project texts.'))
    forward_text.configure(state=DISABLED)
    
    rightframe = ttk.Frame(mainframe,padding='5')
    rightframe.grid(column=2,row=0,sticky=(N,W,E))
    rightframe.columnconfigure(0,weight=1)
    rightframe.rowconfigure(0,weight=1)
    rightframe.rowconfigure(2,weight=1)
    
    empty_frame = ttk.Frame(rightframe,padding='5')
    empty_frame.grid(column=0,row=0,sticky=(N,W,E,S))
    empty_frame.columnconfigure(0,weight=1)
    empty_frame.rowconfigure(0,weight=1)
    
    empty_word_tag = Tkinter.Label(empty_frame, text='Trace Head Word:')
    empty_word_tag.grid(column=0,row=0,sticky=(W,E,N))
    
    environ.empty_word_text = Tkinter.StringVar()
    empty_word_text = Tkinter.Label(empty_frame, textvariable=environ.empty_word_text)
    empty_word_text.grid(column=1,row=0,sticky=(W,E,N))
    
    empty_rbutton = ttk.Radiobutton(empty_frame, text='Set Trace Head Word', variable=environ.work_option, value='trace_head')
    empty_rbutton.grid(column=0,row=1)
    
    environ.empty_options = []
    
    environ.empty_relations = []
    
    empty_tag = Tkinter.Label(empty_frame, text='Co-Indexed Trace and Relations:')
    empty_tag.grid(column=0,row=2,sticky=(W))
    
    hlr1=Frame(rightframe,height=1,bg="black")
    hlr1.grid(column=0,columnspan=2,row=1,sticky='WE')
    
    gap_frame = ttk.Frame(rightframe,padding='5')
    gap_frame.grid(column=0,row=2,sticky=(W,E,S))
    gap_frame.columnconfigure(0,weight=1)
    gap_frame.rowconfigure(0,weight=1)
    
    gap_word_tag = Tkinter.Label(gap_frame, text='Gap Co-index Head:')
    gap_word_tag.grid(column=0,row=0,sticky=(W,E,N))
    
    environ.gap_word_text = Tkinter.StringVar()
    gap_word_text = Tkinter.Label(gap_frame, textvariable=environ.gap_word_text)
    gap_word_text.grid(column=1,row=0,sticky=(W,E,N))
    
    gap_rbutton = ttk.Radiobutton(gap_frame, text='Set Gap Co-index Head', variable=environ.work_option, value='gap_head')
    gap_rbutton.grid(column=0,row=1)
    
    def create_menu():
        def newFile():
            textname = ''
            while textname[-3:] != 'txt':
                textname = tkFileDialog.askopenfilename(filetypes=[('Text files', '.txt')])
                if textname == '':
                    return
            textfile = open(textname)
            environ.texts = read_text(textfile)
            environ.set_file = ''
            while environ.set_file[-3:] != 'cnf':
                environ.set_file = tkFileDialog.askopenfilename(filetypes=[('settings files', '.cnf')])
                if environ.set_file == '':
                    return
            environ.settings = open(environ.set_file)
            environ.settings = list(read_settings(environ.settings))
            environ.relatives = environ.settings.pop()
            environ.pos_output = environ.settings.pop()
            environ.pos_lemmas = environ.settings.pop()
            environ.flags = environ.settings.pop()
            environ.empty = environ.settings.pop()
            environ.syn_rel = environ.settings.pop()
            environ.pos_codes = environ.settings.pop()
            environ.word_db = environ.settings.pop()
            environ.sep_suf = environ.settings.pop()
            environ.ign_file = ''
            while environ.ign_file[-3:] != 'ign':
                environ.ign_file = tkFileDialog.askopenfilename(filetypes=[('ignore files', '.ign')])
                if environ.ign_file == '':
                    return
            environ.ignores = open(environ.ign_file)
            environ.ignores = read_ignore(environ.ignores)
            environ.text_sel = 1
            menubar.entryconfig(1 ,state='normal')            
            menubar.entryconfig(3 ,state='normal')
            previous_text()
        def saveFile():
            output = Namespace()
            output.texts = deTkinter(environ.texts)
            output.text_sel = environ.text_sel
            output.cur_sel = environ.cur_sel.value
            output.set_file = environ.set_file
            output.ign_file = environ.ign_file
            filename = tkFileDialog.asksaveasfilename(filetypes=[('Environment files', '.env')])
            if filename == '':
                return
            else:
                pickle.dump( output, open( filename, 'wb' ) )
        def openFile():
            filename = ''
            while filename[-3:] != 'env':
                filename = tkFileDialog.askopenfilename(filetypes=[('Environment files', '.env')])
                if filename == '':
                    return
            input = pickle.load(open(filename,'rb'))
            environ.texts = reTkinter(input.texts)
            environ.set_file = input.set_file
            environ.settings = open(environ.set_file)
            environ.settings = list(read_settings(environ.settings))
            environ.relatives = environ.settings.pop()
            environ.pos_output = environ.settings.pop()
            environ.pos_lemmas = environ.settings.pop()
            environ.flags = environ.settings.pop()
            environ.empty = environ.settings.pop()
            environ.syn_rel = environ.settings.pop()
            environ.pos_codes = environ.settings.pop()
            environ.word_db = environ.settings.pop()
            environ.sep_suf = environ.settings.pop()
            environ.ign_file = input.ign_file
            environ.ignores = open(environ.ign_file)
            environ.ignores = read_ignore(environ.ignores)
            back_text.configure(state=NORMAL)
            forward_text.configure(state=NORMAL)
            menubar.entryconfig(1 ,state='normal')            
            menubar.entryconfig(3 ,state='normal')
            environ.text_sel = input.text_sel + 1
            previous_text()
            environ.cur_sel.value = input.cur_sel + 1
            word_back()
        def closeFile():
            root.destroy()
        def removeLemma():
            if environ.texts[environ.text_sel].text[environ.cur_sel.value].meta.lemma.get() != '':
                lemma = environ.texts[environ.text_sel].text[environ.cur_sel.value].meta.lemma.get().rstrip('0123456789')
                lnum = environ.texts[environ.text_sel].text[environ.cur_sel.value].meta.lemma.get().lstrip(string.letters + string.punctuation)
                if lnum == '':
                    lnum = '1'
                results = environ.word_db.select(form = environ.texts[environ.text_sel].text[environ.cur_sel.value].ortho, lemma_text = lemma, lemma_num = lnum)
                for result in results:
                    environ.word_db.delete(result)
                environ.texts[environ.text_sel].text[environ.cur_sel.value].lookup = environ.word_db.select(form = environ.texts[environ.text_sel].text[environ.cur_sel.value].ortho.lower())
                find_lemmas()
            
        def removeMorph():
            if environ.texts[environ.text_sel].text[environ.cur_sel.value].pos.get() != '':
                lemma = environ.texts[environ.text_sel].text[environ.cur_sel.value].meta.lemma.get().rstrip('0123456789')
                lnum = environ.texts[environ.text_sel].text[environ.cur_sel.value].meta.lemma.get().lstrip(string.letters + string.punctuation)
                if lnum == '':
                    lnum = '1'
                print lemma
                print lnum
                results = environ.word_db.select(form = environ.texts[environ.text_sel].text[environ.cur_sel.value].ortho, morph_code = environ.texts[environ.text_sel].text[environ.cur_sel.value].pos.get(),lemma_text = lemma, lemma_num = int(lnum))
                for result in results:
                    print result
                    environ.word_db.delete(result)
                environ.texts[environ.text_sel].text[environ.cur_sel.value].lookup = environ.word_db.select(form = environ.texts[environ.text_sel].text[environ.cur_sel.value].ortho.lower())
                find_lemmas()
            
        def addLemma():
            def search(*args):
                for list in lemmas.buttons:
                    for widget in list:
                        widget.destroy()
                results = environ.word_db.select(lemma_text = environ.texts[environ.text_sel].text[environ.cur_sel.value].meta.lemma.get())
                lemmas.results = {}
                for result in results:
                    if result.lemma_num != '1':
                        lemma = result.lemma_text + result.lemma_num
                    else:
                        lemma = result.lemma_text
                    if lemma not in lemmas.results.keys():
                        lemmas.results[lemma] = result.lemma_short_def
                for key in lemmas.results.keys():
                    lemmas.buttons.append([Tkinter.Radiobutton(lemma_options, text=key, variable=lemmas.value, value=key),Tkinter.Label(lemma_options,text=lemmas.results[key])])
                for i in range(len(lemmas.buttons)):
                    lemmas.buttons[i][0].grid(column = 0, row = i+1)
                    lemmas.buttons[i][1].grid(column = 1, row = i+1)
            def exit(*args):
                if lemmas.value.get() == '0':
                    if short_def.get() == '':
                        tkMessageBox.showinfo('Error','You need to provide a definition, so that this lemma can be distinguished from others.')
                        lemma_win.lift()
                    elif environ.texts[environ.text_sel].text[environ.cur_sel.value].meta.lemma.get() == '':
                        tkMessageBox.showinfo('Error','You need to provide text for your lemma.')
                        lemma_win.lift()
                    else:
                        results = environ.word_db.select(lemma_text = environ.texts[environ.text_sel].text[environ.cur_sel.value].meta.lemma.get())
                        current_lemmas = {}
                        for result in results:
                            if result.lemma_num != '1':
                                lemma = result.lemma_text + result.lemma_num
                            else:
                                lemma = result.lemma_text
                            if lemma not in current_lemmas.keys():
                                current_lemmas[lemma] = result.lemma_short_def
                        if current_lemmas != {}:
                            text = 'Did you want one of these instead:\n'
                            for key in current_lemmas.keys():
                                text = text + key + ': ' + current_lemmas[key] + '\n'
                            answer = tkMessageBox.askyesno(title='Confirmation',message=text,icon='question')
                            if answer == True:
                                pass
                            else:
                                addMorph(short_def.get())
                                lemma_win.destroy()
                        else:
                            addMorph(short_def.get())
                            lemma_win.destroy()
                else:
                    environ.texts[environ.text_sel].text[environ.cur_sel.value].meta.lemma.set(lemmas.value.get())
                    addMorph(lemmas.results[lemmas.value.get()])
                    lemma_win.destroy()
            lemmas = Namespace()
            lemmas.buttons = []
            lemmas.value = Tkinter.StringVar()
            lemmas.value.set('0')
            lemma_win = Tkinter.Toplevel(root)
            lemma_win.resizable(0,0)
            lemma_win.protocol("WM_DELETE_WINDOW", exit)
            lemma_win.title = 'Add Lemma'
            lemma_frame = Tkinter.Frame(lemma_win)
            lemma_frame.grid(column=0,row=0)
            lemma_tag = Tkinter.Radiobutton(lemma_frame,text='Lemma Text:',variable=lemmas.value, value='0')
            lemma_tag.grid(column = 0, row = 0)
            lemma_entry = Tkinter.Entry(lemma_frame,textvariable = environ.texts[environ.text_sel].text[environ.cur_sel.value].meta.lemma)
            lemma_entry.grid(column = 1, row = 0) 
            lemma_entry.bind('<Return>', search)
            lemma_tag = Tkinter.Label(lemma_frame,text='Lemma_Short_Def:')
            lemma_tag.grid(column = 2, row = 0)
            short_def = Tkinter.StringVar()
            lemma_short_entry = Tkinter.Entry(lemma_frame,textvariable = short_def)
            lemma_short_entry.grid(column = 3, row = 0)
            lemma_short_entry.bind('<Return>', search)
            lemma_search_button = Tkinter.Button(lemma_frame,text='Search',command=search)
            lemma_search_button.grid(column = 4, row = 0)
            lemma_add_button = Tkinter.Button(lemma_frame,text='Close',command=exit)
            lemma_add_button.grid(column = 5, row = 0)
            lemma_options = Tkinter.Frame(lemma_win)
            lemma_options.grid(column=0,row=1)
        def addMorph(*args):
            record = Namespace()
            try:
                record.short_def = args[0]
                results = environ.word_db.select(lemma_text = environ.texts[environ.text_sel].text[environ.cur_sel.value].meta.lemma.get())
                record.lemma = environ.texts[environ.text_sel].text[environ.cur_sel.value].meta.lemma.get()
                record.lemma_num = 0
                for result in results:
                    if result.lemma_num > record.lemma_num:
                        record.lemma_num = result.lemma_num
                record.lemma_num = str(record.lemma_num + 1)
            except:
                record.lemma = environ.texts[environ.text_sel].text[environ.cur_sel.value].meta.lemma.get().rstrip('1234567890')
                record.lemma_num = environ.texts[environ.text_sel].text[environ.cur_sel.value].meta.lemma.get().lstrip(string.letters + string.punctuation)
                if record.lemma_num == '':
                    record.lemma_num = '1'
                results = environ.word_db.select(lemma_text = record.lemma,lemma_num=record.lemma_num)
                record.short_def = results[0].lemma_short_def
            record.form = environ.texts[environ.text_sel].text[environ.cur_sel.value].ortho.lower()
            def exit():
                record.morph_code = ''
                for slot in slots:
                    record.morph_code = record.morph_code + slot.get()
                environ.word_db.insert(lemma_text=record.lemma,morph_code=record.morph_code,form=record.form,lemma_num=record.lemma_num,lemma_short_def=record.short_def)
                environ.texts[environ.text_sel].text[environ.cur_sel.value].lookup = environ.word_db.select(form = environ.texts[environ.text_sel].text[environ.cur_sel.value].ortho.lower())
                morph_win.destroy()
                find_lemmas()
            morph_win = Tkinter.Toplevel(root)
            #worph_win.resizable(0,0)
            morph_win.protocol("WM_DELETE_WINDOW", exit)
            morph_win.title = 'Add Parse'
            morph_frame = Tkinter.Frame(morph_win)
            morph_frame.grid(column=0,row=0)
            morph_bottom_frame = Tkinter.Frame(morph_win)
            morph_bottom_frame.grid(column=0,row=1)
            slots = []
            radio_buttons = []
            longest = 0            
            full_text = Tkinter.StringVar()
            labels = []
            for i in range(len(environ.pos_codes)):
                if i != 0:
                    new_codes = ['-']+environ.pos_codes[i][1].keys()
                else:
                    new_codes = environ.pos_codes[i][1].keys()
                morph_frame.columnconfigure(i,weight=1)
                slots.append(Tkinter.StringVar())
                slots[-1].set(new_codes[0])
                radio_buttons.append([])
                labels.append(Tkinter.Label(morph_frame,text=environ.pos_codes[i][0]))
                labels[-1].grid(column=i,row=0,sticky='NSWE')
                for j in range(len(new_codes)):
                    key = new_codes[j]
                    if j + 1 > longest:
                        longest = j +1
                    radio_buttons[-1].append(ttk.Radiobutton(morph_frame, text=key, variable=slots[-1], value=key))
                    radio_buttons[-1][j].grid(column=i,row=j+1,sticky='NSWE')
                    if new_codes[j] != '-':
                        radio_buttons[-1][j].bind('<Enter>',lambda e,text=environ.pos_codes[i][1][key]: full_text.set(text))
                    else:
                        radio_buttons[-1][j].bind('<Enter>',lambda e,text='NULL': full_text.set(text))                        
            full_label = Tkinter.Label(morph_bottom_frame, text='Full form: ')
            full_label.grid(column = 0, row = longest + 1,sticky='NSWE')
            
            full_help = Tkinter.Label(morph_bottom_frame, textvariable=full_text)
            full_help.grid(column = 1, row = longest + 1,sticky='NSWE')
            
            morph_close_button = Tkinter.Button(morph_bottom_frame,text='Close',command=exit)
            morph_close_button.grid(column = 2, row = longest+1,sticky='NSWE')
            if environ.texts[environ.text_sel].text[environ.cur_sel.value].meta.lemma.get() == '':
                addLemma()
                morph_win.destroy()
        
        def exportText():
            def check_text():
                for i in range(len(environ.texts[environ.text_sel].text)):
                    word = environ.texts[environ.text_sel].text[i]
                    if word.pos.get() == '':
                        environ.cur_sel.vaule = i
                        tkMessageBox.showinfo(title='Needs more info',message='You need to select a parse.')
                        return 0
                    elif word.meta.head == -1:
                        tkMessageBox.showinfo(title='Needs more info',message='You need to select a syntactic head.')
                        environ.cur_sel.value = i
                        return 0
                    elif word.meta.relation.get() == '':
                        tkMessageBox.showinfo(title='Needs more info',message='You need to select a syntactic relation.')
                        environ.cur_sel.value = i
                        return 0
                return 1
            check_value = check_text()
            if check_value == 1:
                filename = tkFileDialog.asksaveasfilename(filetypes=[('Parsed file', '.psd')])
                psdfile = open(filename,'w')
                build_tree(environ.texts[environ.text_sel],psdfile,(environ.pos_lemmas,environ.pos_output,environ.pos_codes,environ.relatives))
            else:
                environ.cur_sel.value = environ.cur_sel.value + 1
                word_back()
            
        def exportIgnores():
            filename = tkFileDialog.asksaveasfilename(filetypes=[('Ignore files', '.ign')])
            igfile = open(filename,'w')
            igfile.write('SPLIT:' + ','.join(environ.ignores.split) + '\n')
            igfile.write('KEEP:' + ','.join(environ.ignores.keep))
            igfile.close()
        menubar = Menu(root)
        root['menu'] = menubar
        menu_file = Menu(menubar)
        menu_landp = Menu(menubar)
        menu_export = Menu(menubar)
        menubar.add_cascade(menu=menu_file, label='File')
        menu_file.add_command(label='New', command=newFile)
        menu_file.add_command(label='Save', command=saveFile)
        menu_file.add_command(label='Open...', command=openFile)
        menu_file.add_command(label='Close', command=closeFile)
        menubar.add_cascade(menu=menu_landp, label='Lemma and Parse')
        menu_landp.add_command(label='Add Lemma and Parse', command=addLemma)
        menu_landp.add_command(label='Add Parse to Current Lemma', command=addMorph)
        menu_landp.add_separator()
        menu_landp.add_command(label='Remove Lemma', command=removeLemma)
        menu_landp.add_command(label='Remove Parse', command=removeMorph)
        menubar.add_cascade(menu=menu_export, label='Export')
        menu_export.add_command(label='Export Text...', command=exportText)
        menu_export.add_command(label='Export Ignores...', command=exportIgnores)
        menubar.entryconfig(1,state='disabled')        
        menubar.entryconfig(3,state='disabled')
    create_menu()
    root.mainloop()
    
create_root()
