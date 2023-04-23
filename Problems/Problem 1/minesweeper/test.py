from minesweeper import *

random.seed(33)

swoop = Minesweeper()

swoop.print()

sont = Sentence({(0,4), (0,5), (0,6)}, 3)

print(
    sont.known_mines()
)