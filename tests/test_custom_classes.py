import pytest
import ast
from kenken import Kenken, Cage
from custom_classes import Vector, Overlap, VectorSlice
import copy
import itertools
import numpy as np

def test_overlap_class():
    data = [(1,10),(2,20), (3,30)]
    overlap = Overlap(data).to_numpy()

    ## shape 
    assert (overlap.shape == (2,3))
    with pytest.raises(AssertionError):
        assert (overlap.shape != (2,3)) # type overlap:np.ndarray
        assert (overlap.shape != (2,4))

def test_slicing():
    data = [(1,10),(2,20), (3,30)]
    overlap = Overlap(data)
    # test slicing 
    assert (list(overlap[0]) == [1,2,3])
    assert (list(overlap[1]) == [10,20,30])
    with pytest.raises(IndexError):
        assert(list(overlap[42]) == [1,2,3])

    data = [(0,0),(1,1)]
    overlap = Overlap(data)
    assert (list(overlap[0]) == [0,1])
    assert (list(overlap[1]) == [0,1])
    
def test_iteration():
    # test iteration
    data = [(1,10),(2,20), (3,30)]
    overlap = Overlap(data).to_numpy()
    a,b = overlap
    assert (list(b) == [10,20,30])

def test_vector_class_basics():
    data1 = [1,2,3,4]
    data2 = [10,20,30,40]
    data3 = [1,2,3]
    data4 = [1,2,3,4]
    v1 = Vector(data1)
    v2 = Vector(data2)
    v3 = Vector(data3)
    v4 = Vector(data4)
    assert (v1!=v4 and v4!=v1)   # NO TWO VECTORS ARE EQUAL EVER
    assert (v1!=v2 and v2!=v1)
    assert (v1!=v3 and v3!=v1)
    assert (v2!=v3 and v3!=v2)

    with pytest.raises(AssertionError):
        assert (v1==v4 and v4==v1)
        assert (v1==v2 and v2==v1)
        assert (v1==v3 and v3==v1)
        assert (v2==v3 and v3==v2)

    domain = {v1,v2,v4}
    assert (v1 in domain)
    assert (v3 not in domain)

    #ensure set is not counting v1, v4 as two different items
    domain = {v1, v2, v3, v4}
    assert len(domain) == 4
    assert {v1, v2, v3 } != {v1, v2, v3, v4}

def test_other_vector_ops():
    vectors = set(item for item in itertools.product((1,2,3)) if len(set(item))>1)

def test_slicing():
    '''
    A.cells = [(0,0),(1,0),(2,0)]
    B.cells = [(1,1),(2,1),(2,2)]
            ex1    ex2
     012    012     012
    0A     03      04
    1AB    143     123
    2ABB   2542    2545
    '''
    unwrapped_overlap = [(1,0),(2,1), (2,2)]
    overlap = Overlap(unwrapped_overlap)
    position0, position1 = overlap
    assert list(position0) == [1,2,2]
    assert list(position1) == [0,1,2]
    
    v0 = Vector([3,4,5])
    v1 = Vector([3,4,2])
    slice0 = v0[position0]
    slice1 = v1[position1]
    assert isinstance(slice0, VectorSlice)
    assert isinstance(slice1, VectorSlice)
    assert list(slice0) == [4,5,5]
    assert list(slice1) == [3,4,2]

    cage1 = Cage(op='x', target=12, cells = [(0,0), (1,0),(2,0),(3,0),(4,0)], N=8)
    cage2 = Cage(op='+', target=10, cells = [(0,0), (0,1),(0,2)], N=5)
    vector1 = Vector([1,2,3,4,5])
    vector2 = Vector([10,20,30])
    overlap=Overlap([(0,0),])
    assert overlap[0] == np.array([0])


 
def overlap_satisfied(overlap, vector1, vector2):
    x_index, y_index = overlap
    return vector1[x_index] == vector2[y_index]

def test_overlap_satisfied():
    unwrapped_overlap = [(1,0),(2,1), (2,2)]
    overlap = Overlap(unwrapped_overlap)
    position0, position1 = overlap
    # ex1
    v0 = Vector([3,4,5])
    v1 = Vector([3,4,2])
    # ex2
    v2 = Vector([4,2,5])
    v3 = Vector([3,4,5])

    slice0 = v0[position0]
    slice1 = v1[position1]

    assert overlap_satisfied(overlap, v0, v1) # ex 1
    assert not overlap_satisfied(overlap, v2, v3) # ex2


    
    



