#!/usr/bin/env python2
# four_color_sets.py - Take a set of colors $C$ and an integer $p$ and return
# four reasonable subsets of $C$ of size $p$.


def four_color_sets(C, p):
    # We want at least a few extra colors
    assert p <= len(C) - 3, 'p too large for C'
    # Sort C, make an empty set for our output
    Cs = sorted(C)
    sets = set()
    # If we have a lot of colors, do something nice
    if 2 * p + 1 <= len(C):
        # First $p$ colors
        sets.add(frozenset(Cs[:p]))
        # Next $p$ colors
        sets.add(frozenset(Cs[p:2*p]))
        # Overlap those two sets
        sets.add(frozenset(Cs[p//2:3*p//2]))
        # First $p-1$ colors, and one unique color
        sets.add(frozenset(Cs[:p-1] + [Cs[2*p]]))
    # If we don't have a lot of colors, do a cramped version of the same thing
    else:
        # First $p$ colors
        sets.add(frozenset(Cs[:p]))
        # Last $p$ colors
        sets.add(frozenset(Cs[-p:]))
        # Overlap those two sets
        sets.add(frozenset(Cs[(len(C)-p)//2:(p-len(C))//2]))
        # First $p-1$ colors, and last color
        sets.add(frozenset(Cs[:p-1] + [Cs[-1]]))

    return sets

if __name__ == '__main__':
    C = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12}
    p = 6
    for s in four_color_sets(C, p):
        print s
