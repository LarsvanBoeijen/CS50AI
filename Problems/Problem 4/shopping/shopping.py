import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "June", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
VISITOR_TYPES = ["New_Visitor", "Returning_Visitor"]
BOOLEAN = ["FALSE", "TRUE"]


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    # Create lists for evidence and labels
    evidence = []
    labels = []
    
    with open(filename) as f:
        # Create csv Reader object
        reader = csv.reader(f)
        
        # Skip over header line
        next(reader)
        
        # For every row in the dataset
        for row in reader:
            # Cast the data points to their respective data type
            for column, dataPoint in enumerate(row):
                # Administrative, Informational, ProductRelated, Month, OperatingSystems, Browser, Region and TrafficType
                # can all directly be cast as an integer
                if column in [0, 2, 4, 11, 12, 13, 14]:
                    row[column] = int(dataPoint)
                # Turn the month string into a numerical value
                elif column == 10:
                    row[column] = MONTHS.index(dataPoint)
                # Turn VisitorType string into a numerical value: Returning_Visitor = 1, New_Visitor/Other = 0
                elif column == 15:
                    if dataPoint == "Returning_Visitor":
                        row[column] = 1
                    else:
                        row[column] = 0
                # Turn the Weekend and Revenue strings into a numerical value
                elif column in [16, 17]:
                    row[column] = BOOLEAN.index(dataPoint)
                else:
                    row[column] = float(dataPoint)
                    
            # Add everything but the last element to the evidence list
            evidence.append(row[:-1])
            
            # Add the last element to the labels list
            labels.append(row[-1])
    
    return evidence, labels

def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    # Generate the k-nearest neigbor model
    model = KNeighborsClassifier(n_neighbors=1)
    
    # Train model on training set
    model.fit(evidence, labels)
    
    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    # Set up the counts for the number of positive/negative labels as well as how often those labels were correctly identified
    nPositive = 0
    nPositiveCorrect = 0
    nNegative = 0
    nNegativeCorrect = 0
    
    for label, prediction in zip(labels, predictions):
        if label == 0:
            nNegative += 1
            if label == prediction:
                nNegativeCorrect += 1 
        elif label == 1:
            nPositive += 1
            if label == prediction:
                nPositiveCorrect += 1 
    
    # Calculate sensitivity
    sensitivity = nPositiveCorrect / nPositive
    
    # Calculate specificity
    specificity = nNegativeCorrect / nNegative
    
    return sensitivity, specificity


if __name__ == "__main__":
    main()
