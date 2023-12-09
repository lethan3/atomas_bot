import seaborn as sns

from bot import Bot
from field import Field
from game import Game

moves_survived = []
for _ in range(100):
    game = Game(False, Bot())
    game.play()
    print()
    print(len(game.spawned_atoms), game.field.atoms)
    moves_survived.append(len(game.spawned_atoms))

sns.histplot(moves_survived)