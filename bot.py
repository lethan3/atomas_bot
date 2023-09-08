import random

from field import Field, special

class Bot:
    def __init__(self):
        self.fout = open('decisions.txt', 'w+')

    def move(self, field, spawned_atoms, last_atom, op):
        decision = self.decide(field, spawned_atoms, last_atom, op)
        self.fout.write(' '.join(map(str, field.atoms)) + '\n')
        self.fout.write(('1' if len(spawned_atoms) >= 4 and spawned_atoms[-4:].count(-1) == 0 else '0') + ' ')
        self.fout.write(('1' if len(spawned_atoms) >= 19 and spawned_atoms[-19:].count(-2) == 0 else '0') + '\n')
        # self.fout.write(str(len(spawned_atoms)) + ' ' + ' '.join(map(str, spawned_atoms)) + '\n')
        self.fout.write(str(last_atom) + '\n')
        self.fout.write(('1' if op else '0') + '\n')
        self.fout.write(str(decision) + '\n\n')
        self.fout.flush()
        return decision

    def decide(self, field, spawned_atoms, last_atom, op):
        if op: return 1
        if len(field.atoms) == 0: return 0
        
        if (last_atom > 0):
            evals = []
            for i in range(len(field.atoms)):
                test_field = field.copy()
                test_field.place_atom(i, last_atom)
                # print(i, 'test field original: ', test_field.atoms)
                test_field.reduce()
                # print(i, 'test field reduce: ', test_field.atoms)
                evals.append([len(field.atoms) - len(test_field.atoms), test_field.eval_state(), i])
            # print(evals)
            evals.sort(reverse = True)
            return evals[0][2]

        if (last_atom == -1):
            evals = []
            for i in range(len(field.atoms)):
                test_field = field.copy()
                test_field.place_atom(i, last_atom)
                test_field.reduce()
                evals.append([len(field.atoms) - len(test_field.atoms), i])
            evals.sort(reverse = True)
            if (evals[0][0] == -1):
                pluses = []
                for i in range(len(field.atoms)):
                    if (field.atoms[i] == -1):
                        pluses.append(i)
                max_gap, ind = 0, 0
                for i in range(len(pluses)):
                    if (i != len(pluses) - 1):
                        if (pluses[i + 1] - pluses[i] > max_gap):
                            max_gap = pluses[i + 1] - pluses[i]
                            ind = (pluses[i + 1] + pluses[i]) // 2
                    else:
                        if (pluses[0] + len(field.atoms) - pluses[-1] > max_gap):
                            max_gap = pluses[0] + len(field.atoms) - pluses[-1]
                            ind = ((pluses[-1] + pluses[0] + len(field.atoms)) // 2) % len(field.atoms)
                return ind
            return evals[0][1]
        
        if (last_atom == -2):
            ind = 0
            for i in range(len(field.atoms)):
                if (field.atoms[i] > field.atoms[ind]): ind = i
            return ind

        return 0