from tictactoe import *

EMPTY = None

board = initial_state()
board1 = [[EMPTY, X, O],
          [O, X, EMPTY],
          [X, EMPTY, O]]

action = (1,2)

print(
   minimax(board1)
)