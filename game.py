import random

from field import Field, special
from bot import Bot

class Game:
    def __init__(self, display, bot = None):
        self.field = Field(display)
        for i in range(6):
            self.field.place_atom(i, random.randint(1, 3))
        self.spawned_atoms = []
        self.display = display
        self.bot = bot
        
    def dprint(self, *arg):
        if (self.display): print(arg)
                           
    def spawn_atom(self):
        turns = len(self.spawned_atoms)
        l, r = turns // 40 + 1, (turns // 40) * 5 // 4 + 3
        spawned_atom = 0
        if (random.randint(1, 5) == 1 or (len(self.spawned_atoms) >= 4 and self.spawned_atoms[-4:].count(-1) == 0)):
            spawned_atom = -1
        elif (random.randint(1, 20) == 1 or (len(self.spawned_atoms) >= 19 and self.spawned_atoms[-19:].count(-2) == 0)):
            spawned_atom = -2
        elif random.randint(1, 60) == 1:
            spawned_atom = -3
        elif random.randint(1, 90) == 1:
            spawned_atom = -4
        else:
            out_of_range = set()
            for atom in self.field.atoms:
                if atom < l or atom > r:
                    out_of_range.add(atom)
            pick = random.randint(1, 20)
            if (pick == 0):
                spawned_atom = random.choice(list(out_of_range))
            else:
                spawned_atom = random.randint(l, r)
        self.spawned_atoms.append(spawned_atom)
        # self.dprint("Spawned atom:", spawned_atom)
        return spawned_atom
                           
    def turn(self):
        if (len(self.spawned_atoms) % 20 == 0):
            print(end='.',flush=True)
        self.dprint("new turn")
        spawned_atom = self.spawn_atom()
        self.process_spawn(spawned_atom, False)
    
    def process_spawn(self, spawned_atom, op):
        # self.dprint("Processing spawn,", spawned_atom)
        self.field.print_state()
        if self.display:
            print('Turn:', len(self.spawned_atoms), 'Current atom:', spawned_atom if spawned_atom > 0 else special[-spawned_atom], 'Turn into plus:', op)

        inp = self.get_input(spawned_atom, op)
        if (spawned_atom == -2):
            atom = self.field.get_atom(inp)
            self.field.remove_atom(inp)
            self.process_spawn(atom, True)
        elif (spawned_atom == -4):
            atom = self.field.get_atom(inp)
            self.process_spawn(atom, False)
        elif (op):
            self.process_spawn(spawned_atom if inp == 0 else -1, False)
        else:
            self.field.place_atom(inp, spawned_atom)
            self.field.reduce()
                           
    def get_input(self, spawned_atom, op):
        if self.bot is None: return int(input())
        else: return self.bot.move(self.field, self.spawned_atoms, spawned_atom, op)
                           
    def play(self):
        self.field.print_state()
        while (len(self.field.atoms) < 19):
            self.field.print_state()
            self.turn()