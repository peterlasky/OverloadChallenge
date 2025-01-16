import pytest
import sys
from pathlib import Path
# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))
from kenken import Cage, Kenken
from typing import Tuple, List
from custom_classes import Vector

raw_cages = [
    ('-',2,((0,0),(1,0))),
    ('-',1,((0,1),(1,1))),
    ('+',12,((0,2),(0,3),(0,4))),
    ('÷',2,((0,5),(1,5))),
    ('+',11,((2,1),(1,2),(2,2))),
    ('-',2,((1,3),(1,4))),
    ('x',60,((2,0),(3,0),(3,1))),
    ('÷',2,((2,3),(3,3))),
    ('÷',2,((2,4),(3,4))),
    ('x',12,((2,5),(3,5))),
    ('=',1,((3,2),)),
    ('÷',3,((4,0),(5,0))),
    ('+',6,((4,1),(5,1))),
    ('+',5,((4,2),(4,3))),
    ('x',120,((4,4),(4,5),(5,5))),
    ('x',48,((5,2),(5,3),(5,4)))
]
cages = [Cage(*raw_cage,6) for raw_cage in raw_cages]
def test_row_column_fidelity():
    cage = Cage(*raw_cages[4],6)
    d = cage.domain

    # The Domain must be converted to tuples because the 
    # Vector object is not hashable as a normal tuple

    domain = set(tuple(item) for item in cage.domain)
    '''
      01234567
    0
    1   2 
    2  13
    3
    '''
    assert((4,4,3) in domain)# valid
    assert((3,4,4) not in domain) # not valid
    assert((4,3,4) not in domain) # not valid
    assert((5,5,1) in domain) # valid

import math
def test_operation_fidelity():
    for cage in cages:
        op = cage.op
        t = cage.target
        for v in cage.domain:
            if op == 'x': assert(math.prod(v)==t)
            if op == '÷': assert(max(v)/min(v)==t)
            if op == '+': assert(sum(v)==t)
            if op == '-': assert(max(v)-min(v)==t)
        
def test_length():
    for cage in cages:
        assert len(cage.cells) == cage.length
        for v in cage.domain:
            assert len(v) == cage.length

        

