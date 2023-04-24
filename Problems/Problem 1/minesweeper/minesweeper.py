import itertools
import random
import copy


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return self.cells

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        # print(f"Marking {cell} as a mine.")
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        # print(f"Marking {cell} as safe.")
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)
            
    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
              based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
              if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
              if they can be inferred from existing knowledge
        """
        # Mark the cell as a move that has been made
        self.moves_made.add(cell)

        # Mark the cell as safe
        self.mark_safe(cell)
        
        # Determine neigbouring cells on the basis of cell
        neighbours = self.get_neighbours(cell)
        
        # Remove cells whose state has been determined
        for neighbour in neighbours.copy():
            if neighbour in self.mines:
                neighbours.remove(neighbour)
                # Subtract 1 from count if removed cell is a mine
                count -= 1
            elif neighbour in self.safes:
                neighbours.remove(neighbour)
        
        # Add new sentence
        self.knowledge.append(Sentence(neighbours, count))
        
        # While new information can be learned
        while True:
            # Infer additional sentences
            i = 0  
            while i < len(self.knowledge):
                for j in range(len(self.knowledge)):
                    if self.knowledge[i].cells.issubset(self.knowledge[j].cells):
                        inference = Sentence(self.knowledge[j].cells.difference(self.knowledge[i].cells), self.knowledge[j].count - self.knowledge[i].count)
                        if inference not in self.knowledge and inference.cells != set():
                            # print("\nAdding knowledge:")
                            # print(inference)
                            self.knowledge.append(inference)
                i += 1
            
            # Mark new mines and safes
            new_information = False        
            
            for i, knowledge in enumerate(copy.deepcopy(self.knowledge)):
                if knowledge.known_mines() != None:
                    new_information = True
                    for cell in knowledge.known_mines():
                        self.mark_mine(cell)
                
                if knowledge.known_safes() != None:
                    new_information = True
                    for cell in knowledge.known_safes():
                        self.mark_safe(cell)
            
            # Remove empty sentences from the knowledge base
            for sentence in self.knowledge:
                if sentence.cells == set():
                    self.knowledge.remove(sentence)
                    
            # Check for duplicate sentences in the knowledge base
            while self.find_duplicate(self.knowledge)[0] != False:
                self.knowledge.remove(self.find_duplicate(self.knowledge)[1])
            
            # If no new mines or safes have been found, make next move
            if new_information == False:
                break

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        if self.safes.difference(self.moves_made) == set():
            return None
        else:
            safe_move = self.safes.difference(self.moves_made).pop()
            return safe_move

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # Set of all moves
        all_moves = set()
        for i in range(self.height):
            for j in range(self.width):
                all_moves.add((i,j))
        
        # Set of moves all moves not made
        possible_moves = all_moves.difference(self.moves_made)
        
        # Remove known mines
        candidate_moves = possible_moves.difference(self.mines)
        
        if candidate_moves != set():
            return candidate_moves.pop()
        else:
            return None
        
    def get_neighbours(self, cell):
        """
        Returns the set of all neighbouring cells.
        """
        # Create empty list of neighbours
        neighbours = set()
        
        # Add the 3x3 block around cell to neighbours as individual cells
        for i in range(3):
            for j in range(3):
                neighbours.add((cell[0] + (i-1), cell[1] + (j-1)))
                
        # Remove cell and any out of bound cells from neighbours
        for neighbour in neighbours.copy():
            if neighbour == cell or neighbour[0] < 0 or neighbour[0] >= self.height or neighbour[1] < 0 or neighbour[1] >= self.width:
                neighbours.remove(neighbour)
        
        return neighbours
        
        
    def find_duplicate(self, lst):
        for i, x in enumerate(lst):
            for j, y in enumerate(lst):
                if i != j and x == y:
                    return True, x
        return False, Sentence({}, 0)
                