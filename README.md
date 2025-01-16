## Python Operator Overload Challenge: 
### **Extracting a solution from one problem by using the solution code of another.**
Applying multiple student solutions to a well-known CS50AI crossword problem to solve kenken. 

<img src="assets/harvard.png" width="100" style="display: inline-block; margin-right: 10px;">
<img src="assets/img1.png" width="800" style="display: inline-block; margin-bottom: -10px; margin-left: 50px;">  

Here we craft custom classes that allow kenken to use existing crossword solving algorithms through operator overloading.

### Background
This project is a riff on a project from Harvard's online course, *CS50: Introduction to Artificial Intelligence*.  The algorithm takes a blank puzzle structure and a vocabulary and fills in words in a way that is crossword-compatible.  Students were challenged to complete unimplemented methods of `class CrosswordCreator`.  A separate file contains two custom classes describing the layout of a generic crossword puzzle. 

#### **The generic algorithms students are challenged to recreate are not new:**
$\cdot $ ac3 (1977)
$\cdot $ Backtrack search (1950's, likely earlier)

Well trod ground.  Our challenge is not the *CS50* assignment itself.  It is to build a custom Kenken solver that works with student implementation.  Our solution must be *implementation-agnostic*.

#### One rule: Do not modify the students' algorithms.
For a method to be *implementation-agnostic*, it should work with any student's successful implementation of the crossword problem.

#### General approach
The *CS50* source code uses the traditional class name `Variable` to represent a crossword slot (e.g., #3 down, or #4 across, etc.).  A `Crossword` class instance is a collection of `Variable` objects that make up the puzzle. For Kenken, I  created `Cage` and `Kenken` classes to mirror the implementation. To illustrate the general principle with python's `typing` module, any of the solution's constituent functions (here, `func`) must be able to produce the correct effect on both crossword and kenken.  

Example:
<div style="font-size: 14px;">

```python
from typing import Dict, Set, Vector, Tuple, overload
from crossword import Variable, Crossword   # fixed code provided to students
from kenken import Cage, Kenken  # my custom code describing kenken

# it should work for kenken...
@overload  
def func(x: Cage, y: Cage, domains: Dict[Cage, Set[Vector]], overlaps: Overlaps):
    ...

# ... if it works for crossword.
def func(x: Variable, y: Variable, domains: Dict[Variable, Set[str]], 
      overlaps: Dict[Tuple[Variable, Variable], Tuple[int, int]]):
    raise NotImplementedError
```

</div>

#### Did it work?  Yes, until it didn't.  A subtle error, but not mine.
I sampled multiple published solutions to the CS50AI crossword project.  To be solution-agnostic, we consider all possible ways students might approach this problem. While the *Zen of Python* reads:  *"There should be one-- and preferably only one --obvious way to do it,"* the CS50AI students' solutions showed remarkable diversity in their approaches.

**Where / when / how did it fail?**  
Some students *didn't actually implement the `ac3` algorithm correctly* for the original crossword problem.  The `ac3` algorithm is *deterministic*.  While python's `set` ordering might randomize the path of constraint-based reductions of the solution space, the end result must be the same:  The remaining set of possible solutions after applying `ac3` must be the same for all correct implementations of `ac3`. 

**Why the error is easy to miss**
If a faulty ac3 algorithm successfully reduces the domain space correctly but only partially -- i.e, without breaking the solution -- the subsequently applied  `backtrack` algorithm will still solve the puzzle.  And the problem might arise solving one puzzle but not another.  I tested 4 different puzzles in `sanity_check.ipynb`.

**Why it caused my solution to fail**
The faulty ac3 implementations -- the ones that didn't cause the crossword puzzle solver to break -- appear to be breaking my implementation, but only in some cases.   

#### Caveat on my one rule
The solver class, `CrosswordCreator`, contains three methods that cannot reasonably be altered to fit to kenken.
- `print()` and `save()`: these create graphical representations of a crossword puzzle.
- `enforce_node_consistency()`:  There is no obvious way to pass the details of each kenken `Cage` object into the encapsulated `CrosswordCreator`. The limitation is in the constructor which, by my own rule, I cannot edit:
<div style="font-size: 14px;">

```python
class CrosswordCreator():
    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {var: self.crossword.words.copy() for var in self.crossword.variables}
```

</div>

My solution was to override the  python's built-in `dict` class to force the `self.domains` `dict` object to force each `var` object to revaluate itself.  But shorthand instantiation of dictionaries `{}` doesn't behave the same way as `dict()`. I needed to override the built-in `dict` class, but couldn't. Note the difference in types:
<div style="font-size: 14px;">

```python
    >>> class MyDictCls(dict): pass
    >>> builtins.dict = MyDictCls(dict)
    >>> dict1 = dict(a=1, b=2)
    >>> dict2 = {'a':1, 'b':2}    # should be equivalent to dict1
    >>> print(f'{type(dict1)=}\t\t{type(dict2)=}')
    type(dict1)=<class '__main__.MyD'>    type(dict2)=<class 'dict'> 
```

</div>

### How do we recycle the crossword code?
1. Create two classes that closely mirror the crossword puzzle description file, `Crossword.py`:  
- `Cage`: a list of cells, an operator, a target value, and a set of candidate vectors, only one of which will solve the cage and be consistent with all other cages.
- `Kenken`: a list of `Cage` objects, a mapping, `overlaps`, and a method, `neighbors` 

1. Create three new classes to replace generic tuples used in keeping track of various data.  These classes alter and invert the the referencing, the hashing, and the equality representations so that the formulas inside the `CrosswordCreator` give us kenken results. In doing so, these classes 'trick' the crossword algorithm into solving Kenken.

All the *kenken*-specific structures, methods, and properties are inside the *kenken*-class. Inside the KenkenSolver wrapper class, I link the language of the generic solver to the "problem" of *kenken*:

### Testing
I did a battery of `pytests` on my kenken structure to ensure it was working as expected.  
 
### Wrapping
I wrapped each of the students' `CrosswordCreator` class via inheritance to bridge the kenken definition to the crossword solver:

 <div style="font-size: 14px;">

```python
from kenken import Kenken
class KenkenSolver(CrosswordCreator):  # Inherit the ac3 and backtracking algorithms..
    def __init__(self, kenken):
        self.kenken = kenken
        self.crossword = kenken
        self.crossword.variables = self.kenken

        # Constructor copies a complete set vocabulary words for crossword, but == set() for kenken         
        super().__init__(self.kenken)   

        # Here we force node-consistency. 
        # Note: self.super().enforce_node_consistency() is still called, but does not change anything.
        self.domains = {cage: cage.domain for cage in kenken.variables}

        self.print = lambda assignment: pprint(self.kenken, assignment)
        self.save = lambda assignment: None     # for good order
``` 

### Overloading
The key reference the algorithm makes to the Crossword object is the Overlaps dictionary.  Any two
crossword slots (`Variable` objects) either overlap at a single cell, or they don't.  In standard python typing:
<div style="font-size: 14px;">

```python
    overlaps: Dict[Tuple[Variable, Variable]] = Optional[Tuple[int,int]]
    
    overlaps = overlaps[var1, var2] # var1 != var2
    if overlaps is not None:
      index1, index2 = overlaps
      for word1 in self.domains[var1]:
        for word2 in self.domains[var2]:
          overlap_satisfied = val1[index1] == val2[index2]
          ''' In other words:
                  W                     W
                  O               W  O  *  D 2      
              W O R D 2  = True         R        = False
                  D                     D                 
                  2                     2
          '''                  
```

</div>
But in kenken, two cages overlap at multiple points:  
For example, (1,0) means the 1st cell of cage A overlaps with the 0th cell of cage B. 
<div style="font-size: 14px;">

```python                       
    '''
              cages A and B     ex.1       ex.2
                   A              4        5
                   A B B          5 4 6    4 4 6
                   A B            2 3      2 2
                     B              2        3
    '''
```

</div>
Here, based on the cell ordering, `vector1 == (4,5,2)` and `vector2 == (4,3,2,6)` and overlaps are `[(1,0), (1,3), (2,1)]`
That is, if this were in the top left,  the `4` is in `cell(0,0)`, etc., and ```vector2``` occupies, in order, `[(1,1),(2,1),(3,1),(1,2)]`

The overlap does not create a conflict in the first example and but does in the second.  However, we are stuck with the same equation from the legacy code:
<div style="font-size: 14px;">

```python
      val1[position1] == val2[position2]
```

</div>
To make this occasion hold, I created three child numpy array classes: `Overlap`, `Vector`, and `VectorSlice`.  Using the above example:
<div style="font-size: 14px;">

```python
>>> vector1, vector2 = Vector([4,5,2]), Vector([4,3,2,6]) # first example
>>> overlap = Overlap([(1,0),(2,0)])
>>> position1, position2 = overlap  # This indexes into an Overlap object, which returns the transpose

>> position1, position2               
(array([1,1,2]), array([0,3,1]))
>> vector1[position1], vector2[position2]    # now we can index into the vectors. 
(VectorSlice([5,5,2]), VectorSlice([4,6,3]))
>>> vector1[position1] == vector2[position2]  ## Here, with overloaded operators, Overlap is is not in conflict because no conflict exists at the overlap points
True
>>> vector1, vector2 = Vector([5,4,2]), Vector([4,3,2]) # second example
>>> vector1[position1] == vector2[position2] ## Here, a conflict exists at the overlap points
>>> False             
```

</div>

But problems kept arising:
  - Some students added a requirement that no word appear twice in any crossword.  But in Kenken, the same vector of digits can repeat in other cages of the puzzle.  So I embedded each `Vector` object with a id# at instantiation for proper handling of hashing and equalities.  And so `Vector((1,2,3)) != Vector((1,2,3))` if they are not the same object.
  - Hoever, some students applied copy and deepcopy to set objects unnecessarily, so I needed to update the `__copy__()` and `__deepcopy__()` methods to preserve the id# to preserve the hashing and equalities.

### Usage
Use `run.ipynb`.  Self explanatory.

**Note my thanks to github members: *pcoster, hadeeer98, verano_20, iron8kid, marcoshenanz*.  We've never met.  But thanks for your solutions.**
