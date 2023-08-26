from field import Field
from game import Game

game = Game(True, False)
game.play()
print(len(game.spawned_atoms))