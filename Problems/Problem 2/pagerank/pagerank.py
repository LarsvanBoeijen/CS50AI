import os
import random
import re
import sys
import random

DAMPING = 0.85
SAMPLES = 10000

def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")

def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages

def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    probDist = dict()
    
    # Determine random factor
    pRandom = (1-damping_factor)/len(corpus)
    
    for entry in corpus:
        if corpus[page] == set():
            probDist[entry] = 1/len(corpus)
        elif entry in corpus[page]:
            probDist[entry] = damping_factor/len(corpus[page]) + pRandom
        else:
            probDist[entry] = pRandom
    
    return probDist
    
def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Create empty dictionary for the PageRanks
    pageRanks = dict()
    
    # Get the sorted list of all pages
    pages = sorted(corpus.keys())
    
    # Create empty sample
    sample = []
        
    for i in range(0, n):
        # If the list is empty, set a random starting point
        if sample == []:
            sample.append(random.choice(pages))
        else:
            # Get the probability distribution of the previous sample
            probDist = transition_model(corpus, sample[i-1], damping_factor)
            
            # Sample a single observation from the probability distribution and add it to the sample
            sample.append(random.choices(list(probDist.keys()), list(probDist.values()), k = 1)[0])
    
    # Calculate PageRank and add to dictionary
    for page in pages:
        pageRanks[page] = sample.count(page)/n

    return pageRanks

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Determine starting PageRanks
    startRank = 1/len(corpus)
    
    # Create dictionary for PageRanks and set initial values
    pageRanks = {page: startRank for page in corpus}
    
    # Create dictionary for newly calculated PageRanks after each step
    new_pageRanks = {page: None for page in corpus}
    
    # Check for empty pages
    for page in corpus:
        if corpus[page] == set():
            corpus[page] = list(corpus.keys())
    
    # Determine for each page:
    # - Which pages link to it
    # - The number of links on those incoming pages
    network = dict()
    for page in corpus:
        incomingPages = []                                                        
        for otherPage in corpus:
            if page in corpus[otherPage]:
                incomingPages.append((otherPage, len(corpus[otherPage])))
        
        network[page] = incomingPages
        
    
    # Set initial max_change value to enter loop
    max_change = 1
    
    # While the largest change in PageRank is greater than 0.001
    while max_change > 0.001:
        # Reset max_change value
        max_change = 0
        
        # For every page
        for page in corpus.keys():

            # Calculate the summation in the PageRank formula
            summation = 0
            for incomingPage in network[page]:
                summation += pageRanks[incomingPage[0]]/incomingPage[1]
            
            # Calculate new PageRank
            new_pageRanks[page] = (1-damping_factor)/len(corpus) + damping_factor*summation
            
            # Calculate difference in PageRanks and check if difference is new maximum
            difference = abs(pageRanks[page] - new_pageRanks[page])
            if difference > max_change:
                max_change = difference
        
        # Update the pageRanks    
        pageRanks = new_pageRanks.copy()
    
    return pageRanks

if __name__ == "__main__":
    main()
