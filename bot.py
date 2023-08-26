import random

# TODO: Handle empty list case

from field import Field, special

class Bot:
    def __init__():
        pass

    def move(field, spawned_atoms, last_atom, op):
        if op: return 1
        
        if (last_atom > 0):
            evals = []
            for i in range(len(field.atoms)):
                test_field = field.copy()
                test_field.place_atom(i, last_atom)
                test_field.reduce()
                evals.append([len(field.atoms) - len(test_field.atoms), test_field.eval_state(), i])
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
            print(evals)
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