import pytest
import sys
from pathlib import Path
from kenken import Kenken, Cage
from custom_classes import Vector, VectorSlice, Overlap
from pathlib import Path
import copy
from crossword import Crossword

from typing import Tuple, List, Dict, Union
from custom_classes import Vector, VectorSlice, Overlap
n_params = lambda func: len(inspect.signature(func).parameters)

# Choose a solver
from crossword_creators.pcoster import CrosswordCreator
#from crossword_creators.hadeeer98 import CrosswordCreator
#from crossword_creators.sriamin import CrosswordCreator
#from crossword_creators.verano_20 import CrosswordCreator


class KenkenSolver(CrosswordCreator):
    def __init__(self, kenken):
        self.kenken = kenken
        self.crossword = kenken
        self.crossword.variables = self.kenken.cages
        super().__init__(self.kenken)
        self.domains = {cage:cage.domain for cage in kenken.variables}
        self.print = lambda assignment: pprint(self.kenken, assignment)
        self.save = None
    @property
    def size(self):
        return sum([len(d) for d in self.domains])

sys.path.append(str(Path(__file__).parent.parent))
from kenken import Kenken, Cage
from custom_classes import Vector
from typing import Tuple, List

def overlap_satisfied(ols:Union[Overlap, None], x:Cage, y:Cage,val_x:Vector, val_y:Vector)->bool:  
    assert isinstance(ols, (Overlap, type(None)))
    assert isinstance(val_x, Vector), f'val_x is {type(val_x)}, expected Vector. '
    assert isinstance(val_y, Vector)
    if not ols:
        return True
    else:
        x_index, y_index = ols
        if val_x[x_index] == val_y[y_index]:
            return True
        return False

def _overlap_satisfied(_ols:Union[List[Tuple[int, int]], None], x:Cage, y:Cage, val_x:Tuple, val_y:Tuple) -> bool:
    assert isinstance(_ols, (list, type(None)))
    assert isinstance(x, Cage)
    assert isinstance(y, Cage)
    if not _ols: return True
    for pair in _ols:
        assert isinstance(pair, tuple)
        assert len(pair) == 2
        for item in pair:
            assert isinstance(item, int)
    assert isinstance(val_x, Tuple), f'val_x is {type(val_x)}'
    assert isinstance(val_y, Tuple)
    if not _ols:
        return True
    for _ol in _ols:
        position1, position2 = _ol
        if val_x[position1] == val_y[position2]:
            return False
    return True

file = 'tests/test_board3.txt'
kenken = Kenken(file)
solver = KenkenSolver(kenken)
cages= kenken.cages
overlaps = kenken.overlaps
_overlaps = kenken._overlaps
def test_domains():
    for cage, domain in solver.domains.items():
        assert domain is not None
        length = len(list(domain)[0])
        for vector in domain:
            assert (isinstance(vector, Vector))
            assert (len(vector) == length)

def test_satisfieds():
    for c1 in solver.domains.keys(): #cages:
        for c2 in solver.domains.keys():
            if c1 != c2:
                ols = overlaps[c1, c2]
                _ols = _overlaps[c1, c2]
                for v1 in solver.domains[c1]:
                    for v2 in solver.domains[c2]:
                        assert isinstance(v1, Vector)
                        assert isinstance(v2, Vector)
                        t1 = overlap_satisfied(ols, c1, c2, v1, v2)
                        t2 = _overlap_satisfied(_ols, c1, c2, tuple(v1), tuple(v2))
                        assert (t1 == t2)

import numpy as np
def test_overlap_properties():
    for c1 in solver.domains.keys(): #cages:
        for c2 in solver.domains.keys():
            if c1 != c2:
                ols = overlaps[c1, c2]
                if ols is not None:
                    position1, position2 = ols
                    assert(isinstance(position1, np.ndarray))
                    assert(isinstance(position2, np.ndarray))
                    assert(position1.ndim == 1)
                    assert(position2.ndim == 1)
                    assert (all(position1[i] < c1.N for i in range(len(position1))))
                    assert (all(position1[i] >= 0 for i in range(len(position1))))
                    assert (all(position2[i] < c2.N for i in range(len(position2))))
                    assert (all(position2[i] >= 0 for i in range(len(position2))))
                    for vector1 in solver.domains[c1]:
                        for vector2 in solver.domains[c2]:
                            assert isinstance(vector1, Vector)
                            assert isinstance(vector2, Vector)
                            assert isinstance(vector1[position1], VectorSlice)
                            assert isinstance(vector2[position2], VectorSlice)
                            if overlap_satisfied(ols, c1, c2, vector1, vector2):
                                assert vector1[position1] == vector2[position2]
                            else:
                                assert vector1[position1] != vector2[position2]
                        
def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        domains = copy.deepcopy(solver.domains)
        revision = False
        to_remove = set()
        # Iterate over domain of x and y, track any inconsistent x:
        for val_x in self.domains[x]:
            consistent = False
            for val_y in self.domains[y]:
                if val_x != val_y and self.overlap_satisfied(x, y, val_x, val_y):
                    consistent = True
                    break
            if not consistent:
                to_remove.add(val_x)
                revision = True
def test_generic_overlaps():
    overlap = Overlap([(0,0),(1,1),(2,2)])
    vector1 = Vector([1,2,3,4,5])
    vector2 = Vector([1,20,30])
    vector3 = Vector([10,20,30])
    position1, position2 = overlap
    assert vector1[position1] != vector2[position2] # overlap occurs
    assert vector1[position1] == vector3[position2] # overlap does not occur
    assert vector2[position1] != vector3[position2] # overlap occurs
            


