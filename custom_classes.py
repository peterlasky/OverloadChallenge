import numpy as np
from typing import List, Tuple
import itertools

class Overlap(np.ndarray):
    def __new__(cls, input_array: List[Tuple[int, int]]):
        # Convert the input to a NumPy array
        obj = np.asarray(input_array, dtype=int).view(cls)
        assert obj.shape[1] == 2, "Each row must contain exactly 2 elements."
        assert np.issubdtype(obj.dtype, np.integer), "All values must be integers."
        return obj

    def __iter__(self):
        # Use transpose to return a column-wise split of the overlaps
        return iter(np.asarray(self.T))

    def __getitem__(self, key):
        # If the key is an integer, slice column-wise
        assert isinstance(key, int)
        return np.asarray(self).T[key]
   

    def __bool__(self):
        # Return False for an empty array, True otherwise
        return bool(self.size)
    
    def __repr__(self):
        array_str = np.array2string(self)
        return f'Overlap(\n{array_str})'

    def __str__(self):
        return self.__repr__()

    def to_numpy(self):
        return np.asarray(self.T)

    def __copy__(self):
        # Create a shallow copy with the same id
        copied_data = self.tolist()
        new_overlap = self.__class__(copied_data)
        return new_overlap

    def __deepcopy__(self, memo):
        # Create a deep copy with the same id
        if id(self) in memo:
            return memo[id(self)]
        copied_data = self.tolist()
        new_overlap = self.__class__(copied_data)
        memo[id(self)] = new_overlap  # Memoize the new object
        return new_overlap

class VectorSlice(np.ndarray):
    id = itertools.count(0)
    def __new__(cls, input_data):
        obj = np.asarray(input_data, dtype=int).view(cls)
        obj.id = next(cls.id)
        return obj

    def __repr__(self): 
        return f"VectorSlice(id={self.id}, {tuple(i for i in super().tolist())})"

    def __eq__(self, other):
        # Ensure shapes match
        assert self.shape == other.shape, "Shapes of arrays must match"
        assert isinstance(other, VectorSlice)
        # NOTE: #
        ''' Here is the crux of the exercise:  
        for crossword: 
            word1[idx1] == word2[idx2]
                - there is only one overlap point
                - equality means the overlap does not create a conflict

        for kenken:
            vector1[vector_slice1] == vector2[vector_slice2]
                - there are multiple overlap points
                - equality means the overlap DOES create a conflict
        
        Since we're stuck with the crossword_puzzle algorithms,
        we overload the equality such that "Equal" is if no conflict is created.
        '''
        # Return True if no conflict is created (i.e., no elements are equal)
        return not np.any(super().__eq__(other))

    def __ne__(self, other):
        ''' 
        we also have to overload the inequality operator because we can't know what any one 
        student's solution will look like.
        '''
        # Return True if there is a conflict 
        return np.any(super().__eq__(other))

    def __hash__(self):
  
        return hash(tuple(self.flatten()))
        
class Vector(np.ndarray):
    _id_counter = itertools.count(0)  # Renamed to avoid conflict with built-in id()

    def __new__(cls, input_data):
        if not isinstance(input_data, list):
            raise TypeError('Vectors can only be instantiated from list objects')
        if not all(isinstance(element, int) for element in input_data):
            raise TypeError('Vectors can only contain integers')
        obj = np.asarray(input_data, dtype=int).view(cls)
        obj.id = next(cls._id_counter)
        return obj

    def __repr__(self):
        return f"Vector(id={self.id}, {tuple(self.tolist())})"
    
    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        if not isinstance(other, Vector):
            return False
        return self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __copy__(self):
        new_vector = self.__class__(self.tolist())
        new_vector.id = self.id  # Retain the same id
        return new_vector

    def __deepcopy__(self, memo):
        return self.__copy__()

    def __getitem__(self, key):
        result = super().__getitem__(key)
        if isinstance(key, np.ndarray):
            if np.any(key > len(self)):
                raise IndexError(f"Index to Vector Object {self} is out of range")
            if key.ndim == 1:
                return VectorSlice(result)
        else:
            if key > len(self):
                raise IndexError(f"Index to Vector Object {self} is out of range")
        return result

    def __bool__(self):
        return bool(self.size)

    def __len__(self):
        return self.shape[0]

    def __setitem__(self, key, value):
        raise TypeError("Vector instances are immutable")