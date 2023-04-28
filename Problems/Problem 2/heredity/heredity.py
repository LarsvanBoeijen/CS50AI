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
    
    # Get the names of the people in dataset
    names = list(people.keys())

    # Get information needed for looking up the joint probability calculation
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
                
    # Create list for probabilities that will be used in the final calculation of the joint probability
    probabilities = []
    
    # For each person
    for person in names:
        
        # If no parents are listed, use the unconditional probabilities provided
        if all(parent is None for parent in query_info[person]['parents']):
            probGene = PROBS['gene'][query_info[person]['gene']]
        else:
            # Get the genetic makeup of the parents
            genesMother = query_info[query_info[person]['parents'][0]]['gene']
            genesFather = query_info[query_info[person]['parents'][1]]['gene']
        
            # Translate the genetic makeup of the parents into the probabilites of their child receiving a defective gene
            #
            # For each parent, irrespective of their genetic makeup, there are two ways them to pass a defective gene to their child:
            # - A healthy gene is passed which then mutates into a defect gene: P(Healthy) * P(Mutation)
            # - A defect gene is passed which does not mutate: P(Defect) * P(noMutation)
            # Since these two events are mutually exclusive, the probability of their union can be calculated by summing
            # 
            # For each parent, there are three possible genetic makeups:
            # 1) Zero genes: P(Defect passed) = P(Healthy) * P(Mutation) + P(Defect) * P(noMutation) = (1*0.01) + (0*0.99) = 0.01
            # 2) One gene: P(Defect passed) = P(Healthy) * P(Mutation) + P(Defect) * P(noMutation) = (0.5*0.01) + (0.5*0.99) = 0.5
            # 3) Two genes: P(Defect passed) = P(Healthy) * P(Mutation) + P(Defect) * P(noMutation) = (0*0.01) + (1*0.99) = 0.99
            probDefect = []
        
            for genesParent in [genesMother, genesFather]:
                if genesParent == 0:
                    probDefect.append(0.01)
                elif genesParent == 1:
                    probDefect.append(0.5)
                elif genesParent == 2:
                    probDefect.append(0.99)
            
            # Using the probabilities of the parents passing a defective gene, calculate the probability of their child having the specified number of genes
            if query_info[person]['gene'] == 0:
                # P(No defect from mother) * P(No defect from father)
                probGene = (1-probDefect[0]) * (1-probDefect[1]) 
            elif query_info[person]['gene'] == 1:
                # P(Defect from mother) * P(No defect from father) + P(No defect from mother) * P(Defect from father)
                probGene = probDefect[0] * (1-probDefect[1]) + (1-probDefect[0]) * probDefect[1]
            elif query_info[person]['gene'] == 2:
                # P(Defect from mother) * P(Defect from father)
                probGene = probDefect[0] * probDefect[1] 
        
        # Look up relevant conditional probability
        probConditional = PROBS['trait'][query_info[person]['gene']][query_info[person]['trait']]
                
        # Multiply probabilities                
        probabilities.append(probGene * probConditional)
    
    # Calculate joint probability
    for probability in probabilities:
        jointProbability *= probability
        
    return jointProbability


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        if person in one_gene:
            probabilities[person]['gene'][1] += p
        elif person in two_genes:
            probabilities[person]['gene'][2] += p
        else:
            probabilities[person]['gene'][0] += p
            
        if person in have_trait:
            probabilities[person]['trait'][True] += p
        else:
            probabilities[person]['trait'][False] += p

def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        # Get the sums of the probabilities related to gene and trait
        sumGene = sum(list(probabilities[person]['gene'].values()))
        sumTrait = sum(list(probabilities[person]['trait'].values()))
        
        # Determine multiplication factors
        factorGene = 1/sumGene
        factorTrait = 1/sumTrait
        
        # Normalize gene
        for probability in probabilities[person]['gene']:
            probabilities[person]['gene'][probability] *= factorGene

        # Normalize trait
        for probability in probabilities[person]['trait']:
            probabilities[person]['trait'][probability] *= factorTrait
        
if __name__ == "__main__":
    main()
