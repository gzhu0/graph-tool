'''
Collection of graph algorithms
'''

from collections import defaultdict
from itertools import combinations

def adj_list(data: list[list[int]]) -> dict[int, set[int]]:
    '''
    Takes in an edge list and returns an adjacency list
    '''
    output = defaultdict(set)
    for a, b in data:
        output[a].add(b)
        output[b].add(a)
    return dict(output)


def k_cut(data: list[list], k: int) -> list[list[tuple[int,int]]]:
    '''
    Returns a list of each k-cut
    '''
    adj_list = adj_list(data)
    # Testing every possible cut
    # For each cut, we 
    # for potential_cut in combinations(data,k):



    return
