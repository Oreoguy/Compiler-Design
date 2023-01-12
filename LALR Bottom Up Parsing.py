import sys


from tkinter import *

from copy import deepcopy
class State:
    state_count = -1
    def _init_(self, new_state):
        self.state = deepcopy(new_state)
        self.actions = {}
        self.parent = ()
        State.state_count += 1
        self.state_num = self.state_count

    def update_goto(self, X, N):
        self.actions[X] = N.state_num

    def update_parentName(self,I,X):
        self.parent = (I.state_num, X)


class lalrState(State):
    state_count = 0
    def _init_(self,state):
        super(lalrState, self)._init_(state.state)
        self.parent_list = []
        self.actions = deepcopy(state.actions)
        self.parent = deepcopy(state.parent)
        lalrState.state_count += 1

    def update_parentList(self,I):
        self.parent_list.append(I.state_num)

    def update_mapping(self,mapping):
        if self.parent != ():
            self.parent = (mapping[self.parent[0]],self.parent[1])
        for key, val in self.actions.items():
            self.actions[key] = mapping[val]


def term_and_nonterm(grammar,term,non_term):
    for prod in grammar:
        if prod[0] not in non_term:
            non_term.append(prod[0])
        for char in prod[1]:
            if not char.isupper():
                if char not in term:
                    term.append(char)


def calculate_first(grammar,first,term,non_term):
    for t in term:
        first[t] = t;
    for nt in non_term:
        first[nt] = set({})
    for nt in non_term:
        get_first(nt,grammar,first,term)


def get_first(nt,grammar,first,term):
    for prod in grammar:
        if nt in prod[0]:
            rhs = prod[1]
            first_char = rhs[0]
            if first_char in term:
                first[nt].add(first[first_char])
            else:
                for char in rhs:
                    if not first[char] and nt != char:
                        get_first(char,grammar,first,term)

                i = 0
                while i < len(rhs) and 'e' in first[rhs[i]]:
                    for elem in first[rhs[i]]:
                        if 'e' != elem:
                            first[nt].add(elem)
                    i += 1
                if i == len(rhs):
                    first[nt].add('e')
                else:
                    for elem in first[rhs[i]]:
                        first[nt].add(elem)


def get_augmented(grammar,augment_grammar):
    augment_grammar.append([grammar[0][0]+"'",grammar[0][0]])
    augment_grammar.extend(grammar)

def closure(I,augment_grammar,first,non_term):
    while True:
        new_item_added = False
        for item in I:
            cursor_pos = item[1].index('.')
            if cursor_pos == (len(item[1])-1):
                continue
            next_char = item[1][cursor_pos+1]
            if next_char in non_term:
                for prod in augment_grammar:
                    if next_char == prod[0]:
                        if prod[1] == 'e':
                            rhs = 'e.'
                        else:
                            rhs = '.' + prod[1]
                        la = []                                     #look ahead
                        if cursor_pos < (len(item[1]) - 2):
                            Ba = item[1][cursor_pos+2]
                            for firs in first[Ba]:
                                if 'e' == firs:
                                    for elem in item[2]:
                                        if elem not in la:
                                            la.append(elem)
                                else:
                                    if firs not in la:
                                        la.append(firs)
                        else:
                            la = deepcopy(item[2])

                        new_item = [next_char,rhs,la]               #structure of each item
                        
                        if new_item not in I:
                            same_item_with_diff_la = False
                            for item_ in I:
                                if item_[0] == new_item[0] and item_[1] == new_item[1]:
                                    same_item_with_diff_la = True
                                    for las in la:
                                        if las not in item_[2]:
                                            item_[2].append(las)
                                            new_item_added = True
                            if not same_item_with_diff_la:
                                I.append(new_item)
                                new_item_added = True

        if not new_item_added:
            break


def goto(I,X,augment_grammar,first,non_term):
    J =[]
    for item in I:
        cursor_pos = item[1].index('.')
        if cursor_pos < len(item[1])-1:
            next_char = item[1][cursor_pos+1]
            if next_char == X :
                new_rhs = item[1].replace('.'+X,X+'.')
                new_item = [item[0],new_rhs,item[2]]
                J.append(new_item)
    closure(J,augment_grammar,first,non_term)
    return J



def isSame(states,new_state,I,X):
    for J in states:
        if J.state == new_state:
            I.update_goto(X,J)
            return True
    return False



def init_first(augment_grammar,first,non_term):
    I = [[augment_grammar[0][0],'.'+augment_grammar[0][1],['$']]]
    closure(I,augment_grammar,first,non_term)
    return I


def find_states(states,augment_grammar,first,term,non_term):
    first_state = init_first(augment_grammar,first,non_term)
    I = State(first_state)
    states.append(I)
    all_symb = non_term + term
    while True:
        new_state_added =False
        for I in states:
            for X in all_symb:
                new_state = goto(I.state,X,augment_grammar,first,non_term)              #goto(I,X)
                if (new_state != [] ) and not isSame(states,new_state,I,X):
                    N = State(new_state)
                    I.update_goto(X,N)
                    N.update_parentName(I,X)
                    states.append(N)
                    new_state_added = True

        if not new_state_added:
            break


def combine_states(lalr_states,states):
    first = lalrState(states[0])
    first.update_parentList(states[0])
    lalr_states.append(first)
    mapping = [0]
    for I in states[1:]:
        state_found = False
        for J in lalr_states:
            if J.state[0][:2] == I.state[0][:2] :
                state_found = True
                mapping.append(J.state_num)
                J.update_parentList(I)
                for index, item in enumerate(J.state):
                    for la in I.state[index][2]:
                        if la not in item[2]:
                            item[2].append(la)

        if not state_found:
            new_state = lalrState(I)
            new_state.update_parentList(I)

            lalr_states.append(new_state)
            mapping.append(new_state.state_num)

    for I in lalr_states:
        I.update_mapping(mapping)



def get_parse_table(parse_table,states,augmented_grammar):                      #here states -> lalr_states
    ambiguous = False
    for index, I in enumerate(states):
        parse_table.append(I.actions)
        for item in I.state:
            rhs_list = item[1].split('.')
            if rhs_list[1] == '':
                prod_no = augmented_grammar.index([item[0],rhs_list[0]])
                for la in item[2]:
                    if la in parse_table[index].keys():
#                        print('Ambiguous grammar!!')
                        ambiguous = True
                    else:
                        parse_table[index][la] = -prod_no

    if ambiguous:
        print("Ambiguous Grammar!!\n\nGiving priority to Shift over Reduce")


file=open("BT20HCS111.txt", "r")
lines=file.readlines()
lines_list=[]
for l in lines:
    l=(list(l))
    l.remove('\n')
    l="".join(l)
    lines_list.append(l)
    
class Parser():
	
    def _init_(self,win):
        self.grammar = []
        self.augment_grammar = []
        self.first = {}
        self.term = []
        self.non_term = []
        self.states = []
        self.lalr_states = []
        self.parse_table = []
        self.parse_string=""
        self.i=0
        State.state_count = -1
        lalrState.state_count = 0
        #self.l1=Label(win, text='Enter elements')#change later
        #self.l1.place(x=0,y=0)
        self.t2=Text(bd=8,height=50) #displays grammar
        self.b1=Button(win,text='Show Grammar',command=self.print_grammar)
        self.b1.place(x=40,y=150)
        self.t3=Entry() #displays first of grammar
        
        
        l1=Label(win,text="Enter string to be parsed").place(x=0,y=0)
        self.t_in=Entry()
        self.t_in.place(x=40,y=40)
        self.b2=Button(win,text='Submit',command=self.disp_lalr_states,bg='Black',fg='White')
        self.b2.place(x=70,y=70)
        #self.b2=Button(win,text='Show all the LALR states',command=self.disp_lalr_states)
        #self.b2.place(x=120,y=200)
        
    def print_grammar(self):
        self.t2.place(x=0,y=200)
        for l in lines_list:
            self.t2.insert('end',l+'\n') #get rid of \n
            
            
    def read_input(self):
           
        try:
            for line in lines_list:
                line = line.replace(' ' ,'')
        
                if line != '':
                    line_list = line.split('->')
        
                    if line_list[0].isupper() and line_list[1] != '':
                        if '|' in line_list[1]:
                            prod_list = line_list[1].split('|')
                            for prod in prod_list:
                                self.grammar.append([line_list[0],prod])
                        else:
                            self.grammar.append(line_list)
                    else:
                        '''self.t1=Entry()
                        self.t1.place(x=150,y=0)
                        self.t1.delete(0,'end')
                        self.t1.insert("Invalid grammar",'end')'''
                        self.grammar = []
    
            if self.grammar != []:
                term_and_nonterm(self.grammar,self.term,self.non_term)
                calculate_first(self.grammar,self.first,self.term,self.non_term)
                get_augmented(self.grammar,self.augment_grammar)
                find_states(self.states,self.augment_grammar,self.first,self.term,self.non_term)
                combine_states(self.lalr_states, self.states)
                get_parse_table(self.parse_table,self.lalr_states,self.augment_grammar)
                self.changed = False
    
        except (KeyError, IndexError):
            t1=Entry().place(x=0,y=0)
            t1.inser('end',"Invalid grammar")
            self.init()
            
   
    def disp_first(self):
        if self.first == {} or self.changed:
            self.read_input()
        if self.first != {}:
            self.t3.place(x=120,y=200)
            self.t3.delete(0,'end')
            for nonterm in self.non_term:
                temp='First('+nonterm+') : '+' '.join(self.first[nonterm])+','
                self.t3.insert('end',temp)
                
    def disp_lalr_states(self):

        win1=Tk()
        win1.title("LALR States")
        win1.geometry('800x550+50+50')
        t1=Text(win1,bd=10,padx=30,pady=30)
        t1.place(x=0,y=40)
        t2=Entry(win1,width=90)
        t2.place(x=0,y=20)
        b1=Button(win1,text='Show Parsing Table',command=self.disp_parse_table,bg='Black',fg='White')
        b1.place(x=200,y=500)
        if self.lalr_states == [] or self.changed:
            self.read_input()
        if self.lalr_states != []:
            t2.insert('insert',"Number of LALR states : " + str(lalrState.state_count))

            for state in self.lalr_states:
                t1.insert('insert','\n----------------------------------------------------------------')
                if state.state_num == 0:
                    t1.insert('insert',"\nI"+str(state.state_num)+' : \n')
                else:
                    t1.insert('insert',"\nI"+str(state.state_num)+' :'+' goto ( I'+str(state.parent[0])+" , "+ str(state.parent[1])  +" )"+'\n')
                for item in state.state:
                    t1.insert('insert',item[0]+ ' -> ' + item[1]+' ,   [ '+ ' '.join(item[2])+' ]')
                
              
                        
                        
    def disp_parse_table(self):
        win1=Tk()
        win1.title("LALR Table")
        win1.geometry('900x550+50+50')
        t1=Text(win1,bd=100,padx=60,pady=30)
        t1.place(x=0,y=0)
        b1=Button(win1,text='Show Parsing',command=self.disp_parsing,bg='Black',fg='White')
        b1.place(x=200,y=500)
        if self.grammar != []:
            all_symb = []
            all_symb.extend(self.term)
            all_symb.append('$')
            all_symb.extend(self.non_term)
            if 'e' in all_symb:
                all_symb.remove('e')
            head = '{0:12}'.format(' ')
            for X in all_symb:
                head = head + '{0:12}'.format(X)
            t1.insert('insert',head+'\n')
            s = '------------'*len(all_symb)
            t1.insert('insert','\n'+s+'\n')
            for index, state in enumerate(self.parse_table):
                line = '{0:<12}'.format(index)
                print("KK", state)
                for X in all_symb:
                    if X in state.keys():
                        if X in self.non_term:
                            action = state[X]
                        else:
                            if state[X] > 0:
                                action = 's' + str(state[X])
                            elif state[X] < 0:
                                action = 'r' + str(abs(state[X]))
                            elif state[X] == 0:
                                action = 'accept'
                        
                        line = line + '{0:<12}'.format(action)
                    else:
                        line = line + '{0:<12}'.format("")
    
                t1.insert('insert',line)
                t1.insert('insert','\n'+s+'\n')
                
    def parse(self,parse_table,augment_grammar,inpt):
        win1=Tk()
        win1.title("Parsing")
        win1.geometry('600x550+50+50')
        t1=Text(win1,bd=10,padx=30,pady=30)
        t1.place(x=0,y=0)
        inpt = list(inpt+'$')
        stack = [0]
        a = inpt[0]
        try:
            head = '{0:20}'.format("Stack")+'{0:20}'.format("Input")+'{0:20}'.format("Actions")
            t1.insert('insert',head)
            while True:
                string = '\n{0:<20}'.format(''.join(str(stack)))+'{0:<20} '.format(''.join(inpt))
                s = stack[len(stack)-1]
                action = parse_table[s][a]
                print(parse_table)
                print(string,"k", s, parse_table[s][a])
                if action > 0:
                    inpt.pop(0)
                    stack.append(action)
                    t1.insert('insert',string + 'Shift' + a+ '\n')
                    a = inpt[0]
                elif action < 0:
                    prod = augment_grammar[-action]
                    if prod[1] != 'e':
                        for i in prod[1]:
                            stack.pop()
                    t = stack[len(stack)-1]
                    stack.append(parse_table[t][prod[0]])
                    t1.insert('insert',string + 'Reduce ' + prod[0] + ' -> '+ prod[1] + '\n')
                elif action == 0:
                    t1.insert('insert','ACCEPT\n')
                    break
        except KeyError:
            t1.insert('insert','\n\nERROR\n')
            
    def parse_call(self):
        self.parse_string =self.t_in.get()
        self.parse(self.parse_table, self.augment_grammar, self.parse_string)
        
    def disp_parsing(self):
        if self.grammar == [] or self.changed:
            self.read_input()
        if self.grammar != []:
            self.parse_call()
            
            


window=Tk()
mywin=Parser(window)
window.title('LALR(1)')
window.geometry("400x300+10+10")
window.mainloop()