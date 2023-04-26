import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    # Set initial joint probability
    jointProbability = 1
    
    # people is a dictionary of people as described in the “Understanding” section. 
    # The keys represent names, and the values are dictionaries that contain mother and father keys. 
    # You may assume that either mother and father are both blank (no parental information in the data set), 
    # or mother and father will both refer to other people in the people dictionary.
    for person in people:
        print(f"{person}: {people[person]}")
        
    # Get the names of the people in dataset
    names = list(people.keys())
    print(f"\npeople: {names}")
    
    # one_gene is a set of all people for whom we want to compute the probability that they have one copy of the gene.
    one_gene = {'Harry'}
    print(f"\none_gene: {one_gene}")
    
    # two_genes is a set of all people for whom we want to compute the probability that they have two copies of the gene.
    two_genes = {'James'}
    print(f"\ntwo_genes: {two_genes}")
    
    # have_trait is a set of all people for whom we want to compute the probability that they have the trait.
    have_trait = {'James'}
    print(f"\nhave_trait: {have_trait}")
    
    # For any person not in one_gene or two_genes, we would like to calculate the probability that they have no copies of the gene;
    no_genes = [person for person in names if person not in one_gene | two_genes]
    print(f"\nno_genes: {no_genes}")
    
    # For anyone not in have_trait, we would like to calculate the probability that they do not have the trait.
    no_trait = [person for person in names if person not in have_trait]
    print(f"\nno_trait: {no_trait}")
    
    # For anyone with no parents listed in the data set, use the probability distribution PROBS["gene"] 
    # to determine the probability that they have a particular number of the gene.
    no_parents = [person for person in names if people[person]['mother'] == None and people[person]['father'] == None]
    print(f"\nno parents: {no_parents}")
    
    # For anyone with parents in the data set, each parent will pass one of their two genes on to their child randomly, 
    # and there is a PROBS["mutation"] chance that it mutates (goes from being the gene to not being the gene, or vice versa).
    parents = [person for person in names if people[person]['mother'] != None or people[person]['father'] != None]
    print(f"\nparents: {parents}")
    mutationProb = PROBS['mutation']
    
    # Use the probability distribution PROBS["trait"] to compute the probability 
    # that a person does or does not have a particular trait.
    traitProb = PROBS['trait']
    
    # Get information needed for looking up probabilities
    query_info = {
        person: {
            "gene": 0,
            "trait": False,
            "parents": []
        }
        for person in names
    }
    
    for person in names:
        # Set number of genes
        if person in one_gene:
            query_info[person]['gene'] = 1
        elif person in two_genes:
            query_info[person]['gene'] = 2
        
        # Set trait
        if person in have_trait:
            query_info[person]['trait'] = True
            
        # Get parents
        query_info[person]['parents'].append(people[person]['mother'])
        query_info[person]['parents'].append(people[person]['father'])
                
    
    # Calculating the probability that a given person has G number of defective genes:
    #
    # - Each parent is a vase with marbles (genetic material)
    # - Red marbles represent a defect gene
    # - Blue marbles represent a healthy gene
    #
    # - A child's genetic makeup is determined by selecting one marble from each vase
    # - e.g. If two red marbles are selected, two defective genes are passed on to the child
    # 
    # - The genetic makeup of the parents determine how many Red and Blue marbles are in each vase
    # - To compensate for the mutation chance of 1%, a singe defective gene is represented by 99 Red marbles and 1 Blue marble
    # - Similarly, a single healthy gene is represented by 99 Blue marbles and 1 Red marble
    # - So if one parent has two defective genes and the other none, one vase is filled with 198(=2x99) red and 2(=2x1) blue marbles
    #   and the other vase is filled with 198 Blue marbles and 2 Red marbles
    # 
    # - Using this representation, the probability of a parent with two genes and a parent with no genes passing along a single gene
    #   to their child can be thought of as the probability of drawing a marble from a vase with 198 red / 2 blue and another marble
    #   from a vase with 198 blue / 2 red and getting exactly one red marble
    # - This can be done in two ways: RB or BR
    # - The probability of this symmetric difference is (198/200 * 198/200 + 2/200 + 2/200) = 0.9802
    # 
    # - This can be generalised further by seeing the number of red marbles drawn (defective genes passed) as a random variable with the following prob dist:
    # - P(G = 0) = P(Blue_1) * P(Blue_2)
    # - P(G = 1) = P(Blue_1) * P(Red_2) + P(Red_1) * P(Blue_2)
    # - P(G = 2) = P(Red_1) * P(Red_2)
    # - Where P(Red_1), P(Red_2), P(Blue_1), and P(Blue_2) are determined by the distribution of marbles in the vases (genetic material in the parents)
    #
    # - Thus, to determine the probability that a given person has G=g number of defective genes, we do the following:
    #
    # 1) Get the genetic makeup of the parents
    # 2) Translate the genetic makeup into the content of the vases:
    #       - Each defective gene: 99 red, 1 blue
    #       - Each health gene: 99 blue, red
    #       - If genes unknown: 96% chance vase is filled with 198 red/2 blue, 3% chance 100 red/100 blue, 1% chance 198 blue, 2 red --> 193.1 red/6.9 blue --> 1931 red, 69 blue
    # 3) For each vase, determine the probability of drawing a red marble
    # 4) Calculate the probability of drawing G=g number of defective genes when selecting one marble from each vase, using the formulas from the prob dist
    
    
    probabilities = []
    
    # For each person
    for person in names:
        
        # 1) Get the genetic makeup of the parents
        mother = query_info[person]['parents'][0]
        father = query_info[person]['parents'][1]
        
        if mother != None:
            genesMother = query_info[mother]['gene']
        else:
            genesMother = None
            
        if father != None:
            genesFather = query_info[father]['gene']
        else:
            genesFather = None
        
        # 2) Translate the genetic makeup into the content of the vases
        vases = list()
        
        for genesParent in [genesMother, genesFather]:
            if genesParent == 2:
                vases.append((198, 2))
            elif genesParent == 1:
                vases.append((100, 100))
            elif genesParent == 0:
                vases.append((2, 198))
            elif genesParent == None:
                vases.append((1931, 69))
                
        # 3) For each vase, determine the probability of drawing a red marble
        probRed = []
        for vase in vases:
            probRed.append(vase[0]/(vase[0] + vase[1]))
            
        # 4) Calculate the probability of drawing G=g number of defective genes when selecting one marble from each vase
        if query_info[person]['gene'] == 0:
            probGene = (1-probRed[0]) * (1-probRed[1])   # P(Blue_1) * P(Blue_2)
        elif query_info[person]['gene'] == 1:
            probGene = (1-probRed[0]) * probRed[1] + probRed[0] * (1-probRed[1])  # P(Blue_1) * P(Red_2) + P(Red_1) * P(Blue_2)
        elif query_info[person]['gene'] == 2:
            probGene = probRed[0] * probRed[1]   # P(Red_1) * P(Red_2)
        
        # Conditional trait probability
        probConditional = PROBS['trait'][query_info[person]['gene']][query_info[person]['trait']]
                
        # Multiply probabilities                
        probabilities.append(probGene * probConditional)
            
    return jointProbability


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    raise NotImplementedError


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    raise NotImplementedError


if __name__ == "__main__":
    main()
