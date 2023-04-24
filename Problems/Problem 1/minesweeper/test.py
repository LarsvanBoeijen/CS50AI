from minesweeper import *

random.seed(33)

game = Minesweeper()

game.print()

ai = MinesweeperAI()

ai.add_knowledge((0,6), 1)