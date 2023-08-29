import random
import copy

special = ['None', '+', '-', 'D', 'N']

class Field:
    # positive -> element number
    # -1 -> plus atom
    # -2 -> minus
    # -3 -> dark plus
    # -4 -> neutrino

    def __init__(self, display, init_atoms=None):
        if (init_atoms is None): init_atoms = []
        self.display = display
        self.atoms = init_atoms

    def print_state(self):
        if not self.display: return
        print('\n' + '-'*100)
        
        print(end = ' ')
        for atom in self.atoms:
            if (atom > 0):
                print(end='%04s'%(str(atom)))
            else:
                print(end='%04s'%(special[-atom]))
        print()
        for i in range(len(self.atoms)):
            print(end='%04s'%(str(i)))
        print('\n' + '-'*100)
    
    def copy(self):
        return Field(False, copy.deepcopy(self.atoms))
    
    def get_atom(self, ind):
        if len(self.atoms): return self.atoms[ind % len(self.atoms)]
        else: return None
    
    def place_atom(self, ind, num):
        if len(self.atoms): self.atoms.insert(ind % len(self.atoms), num)
        else: self.atoms.insert(0, num)

    def set_atom(self, ind, num):
        if len(self.atoms): self.atoms[ind % len(self.atoms)] = num
        else: raise Exception('Atom set in empty field')

    def remove_atom(self, ind):
        if len(self.atoms): self.atoms.pop(ind % len(self.atoms))
        else: raise Exception('Atom removed in empty field')

    def check_for_reaction(self, ind):
        return (self.get_atom(ind - 1) >= 1 and self.get_atom(ind - 1) == self.get_atom(ind + 1)) or (self.get_atom(ind) == -3 and max(self.get_atom(ind - 1), self.get_atom(ind + 1)) >= 1)

    def reaction(self, ind):
        while len(self.atoms) > 2:
            if (self.check_for_reaction(ind)):
                ind -= 1
                new_atom = max(self.get_atom(ind) + 1, self.get_atom(ind + 1) + 2)
                
                if (self.get_atom(ind) == -3):
                    new_atom = max(self.get_atom(ind - 1) + 3, self.get_atom(ind + 1) + 3)
                elif (self.get_atom(ind) == -1):
                    new_atom = self.get_atom(ind + 1) + 1

                self.set_atom(ind + 1, 0)
                self.set_atom(ind, 0)
                self.set_atom(ind - 1, 0)
                
                for j in range(2):
                    for i in range(len(self.atoms) - 1, -1, -1):
                        if (self.atoms[i] == 0):
                            self.atoms.pop(i)
                            break
                
                for i in range(len(self.atoms)):
                    if (self.atoms[i] == 0):
                        self.set_atom(i, new_atom)
                        ind = i
                        break
            else:
                break
    
    def reduce(self):
        while True:
            if len(self.atoms) <= 2: return
            self.print_state()
            for i in range(len(self.atoms)):
                if (self.check_for_reaction(i)): 
                    self.reaction(i)
                    break
            else:
                break
    
    def eval_state(self):
        eval_vector = []
        for i in range(len(self.atoms)):
            test_field = self.copy()
            test_field.print_state()
            test_field.place_atom(i, -1)
            test_field.reduce()
            eval_vector.append(len(self.atoms) - len(test_field.atoms))
        eval_vector.sort(reverse = True)
        return eval_vector