from generic_kenken import Kenken as CSP
from generic_kenken import Cage as Variable
from generic_kenken import Domain, Vector, Overlap
from typing import Dict, List, Set, Tuple
import copy

Domains_Dict = Dict[Variable, Domain]
class Solver:
    
    def __init__(self, csp:CSP):
        assert isinstance(csp, CSP)
        self.csp = csp

        # pull node-consistent domains
        self.domains: Domains_Dict = {var: var.domain
                                        for var in self.csp}

    def solve(self):
        self.enforce_node_consistency()
        print('domain sizes pre ac3:')
        print([len(self.domains[x]) for x in self.domains])
        self.ac3()
        print('\nDomain sizes after ac3:')
        print([len(self.domains[x]) for x in self.domains])
        return self.backtrack(dict())
    def enforce_node_consistency(self):
        pass

    def ac3(self, arcs=None):
        ''' generic ac3 algorithm '''

        def revise(var1, var2):
            revised = False
            for vector1 in list(self.domains[var1]):
                if not any(self.csp.is_consistent(var1, var2, vector1, vector2) for vector2 in self.domains[var2]):
                    self.domains[var1].remove(vector1)
                    revised = True
            return revised

        if arcs is None:
            arcs = [(var1, var2) 
                    for var1 in self.domains 
                    for var2 in self.domains 
                    if var1 is not var2]
        while arcs:
            (var1, var2) = arcs.pop(0)
            if revise(var1, var2):
                if len(self.domains[var1]) == 0:
                    return False
                for var_n in self.csp.neighbors(var1).difference({var2}):
                    arcs.append((var_n, var1))
        return True
    
    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for var in self.domains:
            if var not in assignment:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for var1 in assignment:
            vector_1 = assignment[var1]

            # Check if there are conflicts between neighboring variables:
            for var2 in self.csp.neighbors(var1):
                if var2 in assignment:
                    vector_2 = assignment[var2]
                    # Check if neighbor variable is assigned and satisfies constraints
                    if not self.csp.overlaps[var1, var2]:
                        continue
                    if not self.csp.is_consistent(var1, var2, vector_1, vector_2):
                        return False
        # Otherwise all assignments are consistent
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        ruleouts = {val: 0 for val in self.domains[var]}

        # Iterate through all possible values of var:
        for val in self.domains[var]:

            # Iterate through neighboring variables and values:
            for other_var in self.csp.neighbors(var):
                for other_val in self.domains[other_var]:

                    # If val rules out other val, add to ruled_out count
                    if not self.csp.overlaps[var, other_var]:
                        continue
                    if not self.csp.is_consistent(var, other_var, val, other_val):
                        ruleouts[val] += 1

        # Return list of vals sorted from fewest to most other_vals ruled out:
        return sorted([x for x in ruleouts], key = lambda x: ruleouts[x])

        # SIMPLE, INEFFICIENT - RETURN IN ANY ORDER:
        #return [x for x in self.domains[var]]

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        # Get set of unassigned variables
        unassigned = set(self.domains.keys()) - set(assignment.keys())

        # Create list of variables, sorted by MRV and highest degree
        result = [var for var in unassigned]
        result.sort(key = lambda x: (len(self.domains[x]), -len(self.csp.neighbors(x))))

        return result[0]


    def backtrack(self, assignment):
        # If all variables are assigned, return assignment:
        if self.assignment_complete(assignment):
            return assignment

        # Otherwise select an unassigned variable:
        var = self.select_unassigned_variable(assignment)
        pre_assignment_domains = copy.deepcopy(self.domains)
        for val in self.order_domain_values(var, assignment):
            assignment[var] = val
            if self.consistent(assignment):
                # Update variable domain to be assigned value
                self.domains[var] = {val}
                # Use ac3 to remove inconcistent values from neighbouring variables
                self.ac3([(other_var, var) for other_var in self.csp.neighbors(var)])
                result = self.backtrack(assignment)
                if result:
                    return result
            # If assignment does not produce solution, remove assignment and reset domains
            del assignment[var]
            self.domains = pre_assignment_domains
        return None
