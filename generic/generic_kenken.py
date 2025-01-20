import itertools
import math

from collections import defaultdict
from functools import cache
import ast
import numpy as np
from typing import List, Tuple, Set, Dict

Vector = Tuple[int,...]
Domain = Set[Vector]
Overlap = List[Tuple[int,int]]

EQUAL, ADD, SUB, MULT, DIV = '=+-x÷'
OP_FUNC = { ADD:   sum, 
            SUB:   lambda x,y: max(x,y)-min(x,y),
            MULT:  math.prod,
            DIV:   lambda x,y: max(x,y)/min(x,y) }
class Cage:
    ''' This class replaces Crossword's Variable class '''
    id_generator = itertools.count(0)
    def __init__(self, op, target, cells, N):
        self.id = next(Cage.id_generator)
        self.target = target
        self.cells = cells
        self.N = N
        self.op = op
        self.set_initial_domain_()

    def set_initial_domain_(self):
        '''In-place operation 

        In Crossword's Variable class, we explore all possible words that might
        fit.  Here, we explore all possible integer tuples (vectors).
        '''
        op: str = self.op; 
        N: int = self.N
        target: int = self.target

        if op == EQUAL:
            domain: Domain = {tuple([target]),}
        elif op in (SUB, DIV):
            domain: Domain = {  tuple([n1, n2])
                        for n1 in range(1, N+1)
                        for n2 in range(1, N+1)
                        if OP_FUNC[op](n1,n2) == target and n1 != n2}
        else: # op in (ADD, MULT)
            rows_occupied, cols_occupied = zip(*self.cells)
            max_duplicates: int = min(len(set(rows_occupied)), len(set(cols_occupied)))
            digit_pool = list(range(1, N+1)) * max_duplicates
            domain: Domain = {
                  permutation # type Tuple
                  for permutation in itertools.permutations(digit_pool, len(self.cells))
                  if self._row_column_constraint_satisfied(permutation)
                     and OP_FUNC[op](permutation) == self.target}
        
        self.domain: Domain = domain
    
    def _row_column_constraint_satisfied(self, perm:Tuple) -> bool:
        rows, cols = defaultdict(set), defaultdict(set)
        for digit, (r, c) in zip(perm, self.cells):
            if digit in rows[r]: 
                return False
            else:
                rows[r].add(digit)
            if digit in cols[c]: 
                return False
            else:
                cols[c].add(digit)
        return True
    
    @property
    def length(self) -> int : # Required: used by crossword solver
        return self.__len__()  
    def __hash__(self):         return hash(self.id)
    def __eq__(self, other):    return self.id == other.id
    def __len__(self):          return len(self.cells)
    def __repr__(self):         return f"{self.id}:{self.op}, {self.target}, {self.cells})" 
    def __str__(self):          return self.__repr__()
    def __copy__(self):         return self

Overlaps = Dict[Tuple[Cage, Cage], Overlap]
class Kenken:
    """ A class to represent a Kenken puzzle as a list of cages """
    
    def __init__(self, structure_file, word_file=None):
        self.structure = []
        with open(structure_file,'r') as f:
            for line in f:
                op, target, cells = ast.literal_eval(line)
                op = {'/':'÷','*':'x',' ':'='}.get(op, op)
                self.structure.append((op, target, cells))
    
        # get the dimension of the puzzle -- 
        self.N = 1 + max(row 
                         for (_, _, cells) in self.structure 
                         for (row, _) in cells)

        # Build cages
        Cage.id_generator = itertools.count(0)
        self.cages = [Cage(op=op, target=target, cells=cells, N=self.N)
                      for (op, target, cells) in self.structure]
        
        self.words = set()  # required during CrosswordCreator initialization

        ### Build overlap dictionary
        '''
        'overlap' maps overlapping cage pairs to their overlapping position. 
        
        For a crossword, any two Variables (cages) can overlap once or not at all. 
        overlap(v1, v2) returns [] or a pair (i,j), meaning the i_th cell of v1 is
        identical to the j_th cell of v2.  

        For Kenken, an overlap(cage1, cage2)= (i,j) means the i_th cell of cage1 shares a
        row or column with the j_th cell.  But there can be multiple overlaps. Here,
        overlaps returns a list of (i,j) overlaps.

        Here, we wrap the output in a custom class, Overlap. See write-up for details
        '''
        from collections import defaultdict
        self.overlaps:Overlaps_Dict = defaultdict(lambda: None)
        for cage1 in self.cages:
            for cage2 in self.cages:
                if cage1 != cage2:  # Don't compute overlaps with self
                    overlap_pts:Overlap = []
                    for position1, cell1 in enumerate(cage1.cells):
                        for position2, cell2 in enumerate(cage2.cells):
                            if cell1[0] == cell2[0] or cell1[1] == cell2[1]:
                                overlap_pts.append((position1, position2))
                    if overlap_pts != []:
                        self.overlaps[(cage1, cage2)] = overlap_pts

    @cache
    def neighbors(self, cage:Cage) -> Set[Cage]:
        """Given a cage, return set of overlapping cages."""
        return {
            other_cage for other_cage in self.cages
            if cage != other_cage and
                self.overlaps[cage, other_cage]
            }

    def is_consistent(self, var1: 'Cage', var2: 'Cage', vector1: Vector, vector2: Vector) -> bool:
        ''' Returns True if vector1 and vector2 are consistent with each other.
        That is, if var1 and var2 share a row or column, then vector1 and vector2
        cannot have the same value in that position.
        '''
        if var1 == var2:
            return True
        overlap = self.overlaps.get((var1, var2), None)
        if overlap is None:
            return True
        for i, j in overlap:
            if vector1[i] == vector2[j]:
                return False
        return True

    def __repr__(self):       return f"Kenken({self.N}x{self.N}, {len(self.cages)} cages)"
    def __iter__(self):       return iter(self.cages)
    def __len__(self):        return len(self.cages)
    def __getitem__(self, i): return self.cages[i]
    def __str__(self):        return self.__repr__()
