from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

base_knowledge = And(
    Or(AKnight, AKnave), # A is either a knight or a knave
    Not(And(AKnight, AKnave)), # A cannot be both a knight and a knave 
)

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    # Structural information
    base_knowledge,
    
    # Problem knowledge
    Implication(AKnight, And(AKnight, AKnave)),
    Implication(AKnave, Not(And(AKnight, AKnave)))
)

def main():
    symbols = [AKnight, AKnave]
    puzzles = [
        ("Puzzle 0", knowledge0)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        
        for symbol in symbols:
            if model_check(knowledge, symbol):
                print(f"    {symbol}")


if __name__ == "__main__":
    main()
