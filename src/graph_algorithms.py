'''
Collection of graph algorithms
'''

from collections import defaultdict
import itertools
import networkx as nx
import itertools

def k_cut(data: list[list], k: int):
    all_edges = [tuple(x) for x in data]
    vertices = set(itertools.chain.from_iterable(data))
    n = len(vertices)
    cut_count = 0
    cuts_return = []

    for cut in itertools.combinations(data, k):
        cut = [tuple(x) for x in cut]
        edges = [x for x in all_edges if x not in cut]

        g = nx.Graph()
        g.add_nodes_from(range(n))
        g.add_edges_from(edges)

        mappings = defaultdict(int)

        contracted = g.copy()
        for component in nx.connected_components(g):
            component = list(component)
            for v in component:
                mappings[v] = component[0]
            for v in component[1:]: # We merge everything to first node
                contracted = nx.contracted_nodes(contracted, component[0], v, self_loops=False)
        # Remapping each vertex
        for u,v in cut:
            new_u = mappings[u]
            new_v = mappings[v]
            contracted.add_edge(new_u,new_v)        
        # Checking bipartite
        is_bip = nx.is_bipartite(contracted)
        if (is_bip): 
            cut_count += 1
            coloring = nx.bipartite.color(contracted)
            set_A = []
            set_B = []
            for v in vertices:
                if coloring[mappings[v]] == 1:
                    set_A.append(v)
                else:
                    set_B.append(v)

                # if mappings[v] in A:
                #     set_A.append(v)
                # elif mappings[v] in B:
                #     set_B.append(v)
            print(set_A,set_B)
            cuts_return.append([set_A, set_B])

    print(cut_count, "cuts found.")
    return cuts_return
