from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Structural knowledge
base_knowledge = And(
    Or(AKnight, AKnave), # A is either a knight or a knave
    Not(And(AKnight, AKnave)), # A cannot be both a knight and a knave
    
    Or(BKnight, BKnave), # B is either a knight or a knave
    Not(And(BKnight, BKnave)), # B cannot be both a knight and a knave
    
    Or(CKnight, CKnave), # C is either a knight or a knave
    Not(And(CKnight, CKnave)), # C cannot be both a knight and a knave 
)

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    base_knowledge,
    
    Implication(AKnight, And(AKnight, AKnave)), # If A is a Knight and thus speaks the truth, he would be both a Knight and a Knave
    Implication(AKnave, Not(And(AKnight, AKnave))) # If A is a Knave and thus lies, he would not be both a Knight and a Knave
    
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    base_knowledge,
    
    Implication(AKnight, And(AKnave, BKnave)), # If A is a Knight, both A and B would be Knaves
    Implication(AKnave, Not(And(AKnave, BKnave))) # If A is a Knave, A and B would not both be Knaves
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    base_knowledge,
    
    Implication(AKnight, Or(And(AKnave, BKnave), And(AKnight, BKnight))), # If A is a Knight, both A and B would be Knaves or Knights
    Implication(AKnave, Not(Or(And(AKnave, BKnave), And(AKnight, BKnight)))), # If A is a Knave, A and B would not both be Knaves or Knights

    Implication(BKnight, Or(And(AKnave, BKnight), And(AKnight, BKnave))), 
    Implication(BKnave, Not(Or(And(AKnave, BKnight), And(AKnight, BKnave)))) 
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    base_knowledge,
    
    Implication(And(BKnight, AKnight), AKnave),
    Implication(And(BKnight, AKnave), AKnight),
    Implication(And(BKnave, AKnight), AKnight),
    Implication(And(BKnave, AKnave), AKnave),
    
    Implication(BKnight, CKnave),
    Implication(BKnave, CKnight),
    
    Implication(CKnight, AKnight),
    Implication(CKnave, AKnave),
    
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
