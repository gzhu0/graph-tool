'''
Script to convert a 3-edge connected graph into a cactus graph
'''

import igraph
import src.graph_algorithms as g

currn = 0

class graph:
    def __init__(self, verticies, edges):
        self.verticies = verticies
        self.edges = edges

def setup(edges):
    # Get vertex balh
    vertices = set()
    for u, v, w in edges:
        vertices.add(u)
        vertices.add(v)
    n = len(vertices)

    # Check for 3ec
    cc = g.k_edge_connected_components(edges,3)
    if cc == [[]] or len(cc[0][0]) != n:
        print("WARNING: Graph is not 3 edge connected")
    
    return vertices

# Crossign cuts
def isCrossing(cut1, cut2):
    '''
    Given 2 cuts as list(set), returns whether they are crossing and a list of intersections
    '''
    A,B = cut1
    C,D = cut2
    intersections = [A & C, A & D, B & C, B & D]
    flag = True
    for i in intersections:
        if len(i) == 0:
            flag = False
    return flag, intersections

def get_f_cuts(vertices, edges):
    '''
    Given (V,E) return all F-cuts
    Returns basic F-cuts
    '''
    # Get all 3 cuts, 4 cuts 
    cuts_3 = g.k_cut(edges, 3)
    cuts_4 = g.k_cut(edges, 4)
    shores_3 = [shore for cut in cuts_3 for shore in cut]
    cuts_3 = [list(map(set, cut)) for cut in g.k_cut(edges, 3)]
    cuts_4 = [list(map(set, cut)) for cut in g.k_cut(edges, 4)]
    shores_3 = [shore for cut in cuts_3 for shore in cut]

    # Get all bridge cuts
    bridge_cuts = []
    for cut in cuts_4:
        for X in cut: # for every shore
            for Y in shores_3: # for every 3-cut shore
                if Y < X: # if Y \in X
                    Y2 = X - Y
                    if Y2 in shores_3:
                        bridge_cuts.append(cut)
    bridge_cuts = list({frozenset(map(frozenset, cut)) for cut in bridge_cuts}) # remove dupes
    bridge_cuts = [list(map(set, cut)) for cut in {frozenset(map(frozenset, cut)) for cut in bridge_cuts}]

    # Get bridge free cuts
    cuts_4_static = {frozenset(map(frozenset, cut)) for cut in cuts_4}
    bridge_cuts_static = {frozenset(map(frozenset, cut)) for cut in bridge_cuts}

    bridgefree_cuts = [list(map(set, cut)) for cut in cuts_4_static - bridge_cuts_static]

    # Get corner cuts
    corner_cuts = []
    for i in range(len(bridgefree_cuts)):
        for j in range(i, len(bridgefree_cuts)):
            crossing, intersections = isCrossing(bridgefree_cuts[i], bridgefree_cuts[j])
            if (crossing):
                for shore in intersections:
                    corner_cuts.append([shore, vertices - shore]) # This is a bit janky but should work

    # Family of F cuts
    F_cuts = []
    F_cuts.extend(cuts_3)
    F_cuts.extend(bridgefree_cuts)
    F_cuts.extend(corner_cuts)
    F_cuts = [list(map(set, cut)) for cut in {frozenset(map(frozenset, cut)) for cut in F_cuts}]

    # Get basic Fcuts
    Basic_F_cuts = []
    for cut1 in F_cuts:
        flag = True
        for cut2 in F_cuts:
            if cut1 != cut2 and isCrossing(cut1, cut2)[0]:
                flag = False
        if flag:
            Basic_F_cuts.append(cut1)

    return F_cuts, Basic_F_cuts

def edit_cuts(v, cuts, dummy, dummyset):
    '''
    Given current vertices, nontrivial basic f cuts, filter them so shores with the dummy node's set are replaced with just the dummy node
    '''
    new_cuts = []
    for s1,s2 in cuts:
        s1 = s1 & v
        s2 = s2 & v
        if dummyset <= s1: 
            s1.add(dummy)
        elif dummyset <= s2:
            s2.add(dummy)
        if len(s1) > 0 and len(s2) > 0:
            new_cuts.append((s1,s2))
    return new_cuts

def cactus(verticies, Fcuts, bFcuts, e):
    '''
    Recursive cactus function that returns a graph struct
    Takes in verticies, basic f-cuts
    '''
    v = verticies
    global currn
    n = len(v)
    # Base Case: Vertex 
    if len(v) == 1:
        return graph(verticies = v, edges = [])

    # Check if there exists a nontrivial basic cut. If there is, then partition, create dummy nodes, and recurse
    for cut in bFcuts:
        shore1, shore2 = cut
        p1 = shore1 & v # p - partitions
        p2 = shore2 & v

        print("CUT", shore1, shore2)
        print("PARTITIONS", p1,p2)
        if len(p1) >= 2 and len(p2) >= 2: # The cut is partitioning the subgraph, so we recurse

            # Add dummy nodes
            a = currn + 1
            b = currn + 2
            currn += 2
            # Partition verticies
            v1 = p1 | {a} 
            v2 = p2 | {b}

            new_Fcuts1 = edit_cuts(v1,Fcuts,a,p2)
            new_Fcuts2 = edit_cuts(v2,Fcuts,b,p1)

            new_bFcuts1 = edit_cuts(v1,bFcuts,a,p2)
            new_bFcuts2 = edit_cuts(v1,bFcuts,b,p1)

            cactus1 = cactus(v1, new_Fcuts1, new_bFcuts1,e)
            cactus2 = cactus(v2,new_Fcuts2, new_bFcuts2,e)

            verticies = cactus1.verticies | cactus2.verticies #union
            edges = cactus1.edges + cactus2.edges + [(a,b)]

            return graph(verticies = verticies, edges = edges)
    # All 3-cuts are trivial, so we do checks:
    
    # Check if the graph is cubic
    degrees = {_v : 0 for _v in v}
    print(degrees)
    for u,v,w in e:
        print(u,v)
        degrees[u] += 1
        degrees[v] += 1
    if all(d == 3 for d in degrees.values()):
        print("graph is cubic!")
        return graph(verticies = verticies, edges = edges)

    # Else there is a cycle
    # Since every cactus node is empty or single it should be safe to treat everythig as a single vertex? and we use F cuts i thnk

    new_edges = []
    corners = None
    flag2 = False
    # 1. Find Crossing cuts
    for i in range(len(Fcuts)):
        for j in range(i,len(Fcuts)):
            flag, corners = isCrossing(Fcuts[i],Fcuts[j])
            # Corners from isCrossing should be in a cycle order
            if flag:
                flag2 = True 
                break 
        if flag2: break
    if not flag:
        raise ValueError("Crossing cuts not found")

    # 2. Get node ordering for the cycle
    for i in range(len(corners)):
        new_edges.append((corners[i], corners[(i+1)%len(corners)]))

    return graph(verticies=verticies, edges=new_edges)
 
def create_cactus(edges):
    global currn
    '''
    Creates a cactus given edges
    Oh my balls this better work
    '''
    vertices = setup(edges)
    currn = len(vertices) # Global counter
    F_cuts, basic_F_cuts = get_f_cuts(vertices, edges)
    cactus_graph = cactus(vertices, F_cuts, basic_F_cuts, edges)
    result = [list(edge) for edge in cactus_graph.edges]
    print("Generated", result)
    result = [(list(s1)[0], list(s2)[0]) for s1, s2 in result]

    return result

