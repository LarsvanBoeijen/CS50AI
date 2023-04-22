"""
Tic Tac Toe Player
"""

import math
import copy
# import os

# os.environ["SDL_VIDEODRIVER"] = "x11"

X = "X"
O = "O"
EMPTY = None

class Node():
    def __init__(self, state, parent, action):
        self.state = state
        self.parent = parent
        self.action = action


class StackFrontier():
    def __init__(self):
        self.frontier = []

    def add(self, node):
        self.frontier.append(node)

    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node


class QueueFrontier(StackFrontier):

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node

def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]

def player(board):
    """
    Returns player who has the next turn on a board.
    """
    # Flatten the board
    flattened_board = [item for sublist in board for item in sublist]
    
    # Check for intial board state
    if all(space == EMPTY for space in flattened_board):
        return X
    # Else check whose turn it is by determining how many turns X and O have had
    else:
        turns_X = sum(space == X for space in flattened_board)
        turns_O = sum(space == O for space in flattened_board)
        
        if turns_X == turns_O:
            return X
        else:
            return O

def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions = set()
    for i, row in enumerate(board):
        for j, space in enumerate(row):
            if space == EMPTY:
                actions.add((i, j))

    return actions

def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    # Check for invalid move
    if action not in actions(board):
      raise Exception("Invalid move entered")

    # Create a copy of the current board state
    new_board = copy.deepcopy(board)
    
    # Complete the action
    if player(board) == X:
        new_board[action[0]][action[1]] = X
    else:
        new_board[action[0]][action[1]] = O
        
    return new_board
    

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Check for horizontal lines
    for row in board:
        if all(space == row[0] for space in row):
            return row[0]
    
    # Transpose the board and check for vertical lines
    transposed_board = list(map(list, zip(*board)))
    for row in transposed_board:
        if all(space == row[0] for space in row):
            return row[0]
            
    # Flip the board and check for diagonal lines
    flipped_board = board[::-1]
    diagonals = [[], []]
    for i in range(3):
     diagonals[0].append(board[i][i])
     diagonals[1].append(flipped_board[i][i])
    
    for diagonal in diagonals:
         if all(space == diagonal[0] for space in diagonal):
            return diagonal[0]
    
    # If no winner is found return None
    return None

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # Create flattened board
    flattened_board = [item for sublist in board for item in sublist]
        
    # Check for a winner or a full board
    if winner(board) in (X, O) or all(space != EMPTY for space in flattened_board):
        return True
    else:
        return False

def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    # Check for terminal board
    if terminal(board):
        return None
        
    alpha = -1
    beta = 1
        
    if player(board) == X:
        max_X = max_value(board, alpha, beta)
        
        for action in actions(board):
            if min_value(result(board, action), alpha, beta) == max_X:
                return action
    else:
        min_O = min_value(board, alpha, beta)
        
        for action in actions(board):
            if max_value(result(board, action), alpha, beta) == min_O:
                return action

def max_value(board, alpha, beta):
    if terminal(board):
        return utility(board)
    
    best_value = -math.inf
    
    for action in actions(board):
        value = min_value(result(board, action), alpha, beta)
        best_value = max(best_value, value)
        alpha = max(alpha, best_value)
        if beta <= alpha:
            break
        
    return best_value
    
def min_value(board, alpha, beta):
    if terminal(board):
        return utility(board)
    
    best_value = math.inf
    
    for action in actions(board):
        value = max_value(result(board, action), alpha, beta)
        best_value = min(best_value, value)
        beta = min(beta, best_value)
        if beta <= alpha:
            break
    
    return best_value