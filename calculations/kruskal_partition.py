"""
Entropy-weighted partitioning, and Boruvka's parallel rounds.

Article : Where the Research Areas Converge  (Sections 09-10, 23; Figures 6, 12)
Claims  : Stopping Kruskal after n-k edges gives k partitions directly.
          Boruvka reaches the same tree in log2(n) parallel rounds.
"""
import math
print(__doc__)
edges = [("A","B",0.95),("B","C",0.88),("A","C",0.91),("D","E",0.92),
         ("E","F",0.86),("G","H",0.90),("C","D",0.12),("F","G",0.08),("C","H",0.05)]
nodes = sorted({n for a,b,_ in edges for n in (a,b)})

def uf(nodes):
    p = {n:n for n in nodes}
    def find(x):
        while p[x] != x: p[x] = p[p[x]]; x = p[x]
        return x
    return p, find

def kruskal(k):
    p, find = uf(nodes); added = 0; tree = []
    for a,b,w in sorted(edges, key=lambda e: -e[2]):
        if find(a) != find(b):
            if added == len(nodes)-k: break
            p[find(a)] = find(b); added += 1; tree.append((a,b,w))
    comp = {}
    for n in nodes: comp.setdefault(find(n), []).append(n)
    return tree, sorted(sorted(g) for g in comp.values())

print("Kruskal, descending, stopping early")
print("-" * 58)
for k in (1,2,3,4):
    tree, parts = kruskal(k)
    print(f"  k={k}: {len(tree)} edges added -> {parts}")

print("\n  The intermediate state of the algorithm IS the partitioning.")
print("  No need to build the tree and cut it apart afterwards.\n")

_, parts = kruskal(3)
grp = {n:i for i,g in enumerate(parts) for n in g}
cross = [(a,b,w) for a,b,w in edges if grp[a] != grp[b]]
tot = sum(w for _,_,w in edges); cw = sum(w for _,_,w in cross)
print("Bandwidth across the partition boundaries at k = 3")
print("-" * 58)
for a,b,w in cross: print(f"  {a}-{b}  {w}")
print(f"  total entanglement in the network : {tot:.2f}")
print(f"  crossing the boundaries           : {cw:.2f}  ({100*cw/tot:.1f}%)")
print("  Note this counts every crossing edge, not only tree edges.")

def boruvka(k):
    p, find = uf(nodes); rounds = 0
    while True:
        comp = {}
        for n in nodes: comp.setdefault(find(n), []).append(n)
        if len(comp) <= k: break
        best = {}
        for a,b,w in edges:                       # all components at once
            ra, rb = find(a), find(b)
            if ra == rb: continue
            for r in (ra, rb):
                if r not in best or w > best[r][2]: best[r] = (a,b,w)
        if not best: break
        rounds += 1
        for a,b,w in set(best.values()):
            if find(a) != find(b): p[find(a)] = find(b)
    comp = {}
    for n in nodes: comp.setdefault(find(n), []).append(n)
    return rounds, sorted(sorted(g) for g in comp.values())

print("\nBoruvka: every component finds its best outgoing edge at once")
print("-" * 58)
r, parts = boruvka(3)
print(f"  parallel rounds: {r}   partitions: {parts}")
print("  Same answer as Kruskal, reached differently.\n")
print("  Kruskal needs one global sort, then sequential processing.")
print("  Boruvka needs at most log2(n) rounds:")
for n in (8, 100, 10_000, 1_000_000):
    print(f"    {n:>9,} nodes -> at most {math.ceil(math.log2(n)):2d} rounds")
