import math
import itertools

x = math.comb(4,2)

print(x)

# def probability_red_marbles(n_red_1, n_blue_1, n_red_2, n_blue_2, n_red_drawn):
#     # Total number of ways to draw n_red_drawn marbles from each vase
#     total_ways = math.comb(n_red_1 + n_blue_1, n_red_drawn) * math.comb(n_red_2 + n_blue_2, n_red_drawn)
    
#     # Number of ways to draw exactly n_red_drawn red marbles
#     ways_red = math.comb(n_red_1, n_red_drawn) * math.comb(n_blue_2, n_red_drawn) + math.comb(n_blue_1, n_red_drawn) * (n_red_2, n_red_drawn)
    
#     # Probability of drawing exactly n_red_drawn red marbles
#     prob_red = ways_red / total_ways
    
#     return prob_red
    
# prob = probability_red_marbles(198, 2, 2, 198, 1)
# print(prob)






