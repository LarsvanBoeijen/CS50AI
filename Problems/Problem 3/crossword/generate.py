import sys
import math
import copy

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # Loop over the domain of each variable, throwing out words that fail the length constraint
        for variable in self.domains:
            for word in self.domains[variable].copy():
                if len(word) != variable.length:
                    self.domains[variable].remove(word)
        
    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # Check for overlap between variables
        overlap = self.crossword.overlaps[x,y]
        
        # If there is no overlap, there is no possibility of conflict
        if overlap == None:
            return False
        
        # Set initial revised status
        revised = False
        
        # For each word in the domain of x
        for word in self.domains[x].copy():
            # Set initial constraint satisfaction to 0
            constraint = 0    
            for otherWord in self.domains[y]:
                
                # Check whether the constraint is satisfied
                if word != otherWord and word[overlap[0]] == otherWord[overlap[1]]:
                    constraint = 1
                    break
            
            if constraint == 0:
                self.domains[x].remove(word)
                revised = True
        
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # If no arcs passed, fill queue with initial list of all arcs
        if arcs == None:
            arcs = [arc for arc, overlap in self.crossword.overlaps.items() if overlap != None]
            
        # While the list of arcs is not empty
        while len(arcs) != 0:
            # Pop arc from the list
            arc = arcs.pop()
            
            # Check whether variable needs to be revised
            if self.revise(arc[0], arc[1]):
                # If domain is empty, then arc consistency not possible
                if len(self.domains[arc[0]]) == 0:
                    return False
                # Add additional arcs to ensure arc consistency
                for z in self.crossword.neighbors(arc[0]) - {arc[1]}:
                    arcs.append((z,arc[0]))
                    
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for variable in self.domains:
            if variable not in assignment:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # For each assigned variable
        for variable in assignment:
            # Check assigned values for duplicates
            for otherVariable in assignment:
                if variable != otherVariable and assignment[variable] == assignment[otherVariable]:
                    return False
            
            # Check whether each word is of the right length
            if len(assignment[variable]) != variable.length:
                return False
            
            # Check for arc concistency between variables currently assigned
            # Consider each neighbour
            for neighbour in self.crossword.neighbors(variable):
                # If the neighbour is not assigned a value yet, move to the next neigbour
                if neighbour not in assignment:
                    continue
                
                # Get the overlapping cell
                overlap = self.crossword.overlaps[variable, neighbour]
                    
                # Check for a conflict between assignments
                if assignment[variable][overlap[0]] != assignment[neighbour][overlap[1]]:
                    return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # Create list for tuples containing each word in the dictionary and the number of values they rule out
        tuples = []
        
        # Get the domain of the variable
        domain = self.domains[var]
        
        # Get the unassigned neighbours of the variable
        neighbours = self.crossword.neighbors(var)
        for neighbour in neighbours.copy():
            if neighbour in list(assignment.keys()):
                neighbours.remove(neighbour)
        
        # For every word in the domain of the variable
        for word in domain:
            
            # Start the count of ruled out values
            ruledOut = 0
            
            # If the word is not yet assigned
            if word not in list(assignment.values()):
                
                # For every neighbour
                for neighbour in neighbours:
                    # Get the overlapping cell
                    overlap = self.crossword.overlaps[var, neighbour]
                    
                    # If the word is in the domain of the neighbour or conflicts with any of the neigbour's choices, add one to the count
                    for otherWord in self.domains[neighbour]:
                        if word == otherWord or word[overlap[0]] != otherWord[overlap[1]]:
                            ruledOut += 1
                        
            tuples.append((word, ruledOut))
        
        # Order the list of tuples by the number of values they rule out
        orderedTuples = sorted(tuples, key=lambda x: x[1])
        
        # Extract the words from in the list of tuples in order
        orderedValues = [tuple[0] for tuple in orderedTuples]
        
        return orderedValues

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # Get the list of all variables
        variables = list(self.domains.keys())
        
        # Set fewest remaining words
        fewestRemaining = math.inf
        
        # For every variable
        for variable in variables.copy():
            # Exclude any variable already assigned
            if variable in assignment.keys():
                continue
            # If the inspected variable has less words in its domain than the current fewest, select that variable
            else:
                if len(self.domains[variable]) <= fewestRemaining:
                   
                    # Check for a tie
                    if len(self.domains[variable]) == fewestRemaining:
                        
                        # Check whether the inspected variable has more neighbours the the currently selected variable
                        if self.crossword.neighbors(variable) > self.crossword.neighbors(selectedVariable):
                            selectedVariable = variable
                    else:
                        # Set the new fewest
                        fewestRemaining = len(self.domains[variable])
                        
                        # Set the new selected variable        
                        selectedVariable = variable

        return selectedVariable

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # Check for complete assignment
        if self.assignment_complete(assignment):
            return assignment
        
        # Select a variable
        selectedVariable = self.select_unassigned_variable(assignment)
        
        # Create newAssignment
        newAssignment = copy.deepcopy(assignment)
        
        # Get the ordered domain
        orderedDomain = self.order_domain_values(selectedVariable, assignment)
        
        # Loop over values in the selected variables' domain
        for value in orderedDomain:
            
            # Assign the value to the variable
            newAssignment[selectedVariable] = value
            
            # If the value is consistent
            if self.consistent(newAssignment):
                # Assign the value
                assignment[selectedVariable] = value
                
                # Get the arcs involving the selected variable
                selectedArcs = [arc for arc, overlap in self.crossword.overlaps.items() if overlap != None and arc[0] == selectedVariable]
                
                # Ensure arc consistency between selected arcs
                self.ac3(arcs=selectedArcs)
            
                # Backtrack
                result = self.backtrack(assignment)
                
                # If the result was not a failure, return the result
                if result != None:
                    return result
            
        return assignment

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
