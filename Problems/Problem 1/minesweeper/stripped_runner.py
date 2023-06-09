import pygame
import sys
import time

import random
random.seed(33)

from minesweeper import Minesweeper, MinesweeperAI

HEIGHT = 8
WIDTH = 8
MINES = 8

# Colors
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
WHITE = (255, 255, 255)

# Create game and AI agent
game = Minesweeper(height=HEIGHT, width=WIDTH, mines=MINES)
ai = MinesweeperAI(height=HEIGHT, width=WIDTH)

# Keep track of revealed cells, flagged cells, and if a mine was hit
revealed = set()
flags = set()
lost = False

game.print()

moves = [
    (0,7),
    (1,6),
    (1,7)
]

for move in moves:
    if move:
        print("\nCurrent knowledge:")
        for knowledge in ai.knowledge:
            print(knowledge)
        
        print(f"\nMade move: {move}")
        if game.is_mine(move):
            lost = True
        else:
            nearby = game.nearby_mines(move)
            revealed.add(move)
            ai.add_knowledge(move, nearby)
        
        print("\nKnown mines:")
        for mine in ai.mines:
            print(mine)
            
        print("\nKnown safes:")
        for safe in ai.safes:
            print(safe)

print("Random move:")
print(ai.make_random_move())


# print(move)

# move = ai.make_safe_move()
# if move is None:
#     move = ai.make_random_move()
#     if move is None:
#         flags = ai.mines.copy()
#         print("No moves left to make.")
#     else:
#         print("No known safe moves, AI making random move.")
# else:
#     print("AI making safe move.")
# time.sleep(0.2)

# Make move and update AI knowledge


