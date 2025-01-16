import sys
import itertools
import copy
from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # For loop each variable and intialize empty set for word that do not follow node consistency.
        for variable in self.domains:
            remove_words = set()

            # Loop thru each word in variables domain, all while checking for node consistency.
            for word in self.domains[variable]:
                if len(word) != variable.length:
                    remove_words.add(word)

            # If a word doesn't meet node consistency, remove from variable domain.
            # All while using a for loop to interate over the words.
            for word in remove_words:
                self.domains[variable].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # Create variables revision and overlap and assign them.
        revision = False
        overlap = self.crossword.overlaps[x, y]

        # Domain check for x's, if there is a overlap between the x, y values.
        if overlap is not None:

            # Initialize set of words to remove from the x's domain base.
            remove_words = set()

            # For loop, to interate over the word in the x's domain.
            for x_domain in self.domains[x]:
                overlap_wordx = x_domain[overlap[0]]
                overlap_wordy = {i[overlap[1]] for i in self.domains[y]}

                # No value in y's domains, that also doesn't conflict.
                if overlap_wordx not in overlap_wordy:
                    remove_words.add(x_domain)
                    revision = True

            # In X's domain remove words.
            for word in remove_words:
                self.domains[x].remove(word)

        return revision

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # If statement, if all arc variables with overlap in the crossword.
        # Check for arc consistency.
        if arcs is None:
            arc_queue = list(itertools.product(self.crossword.variables, self.crossword.variables))
            arc_queue = [arc for arc in arc_queue if arc[0] != arc[1] and self.crossword.overlaps[arc[0], arc[1]] is not None]
        else:
            arc_queue = arcs

            # Queue is not empty, repeat the loop.
            while arc_queue:
                arc = arc_queue.pop(0)
                x, y = arc[0], arc[1]

                # The variables in arc_queue x, y are arc consistent.
                if self.revise(x, y):

                    # Domain is empty, return false.
                    if not self.domains[x]:
                        print("Error Ac3")
                        return False

                    # Add arcs to arc_queue, once finshed changing to domain.
                    # This will ensure arcs stay arc consitent by using a for loop to interate throughout the domain.
                    for j in (self.crossword.neighbours(x) - {y}):
                        arc_queue((z, x))

            return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # If statement, if the assignment is complete each variable key in the assignment dictionary.
        # Corresponding value/key is not empty string of characters.
        if set(assignment.keys()) == self.crossword.variables and all(assignment.values()):
            return True
        else:
            return False

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # If statement so that if not all values keys in the crossword aren't distinct/conflict.
        if len(set(assignment.values())) != len(set(assignment.keys())):
            return False

        # # If statement so that if not all values keys in the crossword aren't the correct length.
        if any(variable.length != len(word) for variable, word in assignment.items()):
            return False

        # For loop, to check for inconsistent variable that are between neighbours.
        for variable, word in assignment.items():
            for neighbor in self.crossword.neighbors(variable).intersection(assignment.keys()):
                overlap = self.crossword.overlaps[variable, neighbor]

                # If the word of the overlap[0] doesnt equal to the neighbor overlap[1], return False.
                if word[overlap[0]] != assignment[neighbor][overlap[1]]:
                    return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # Dictionary store number of choices that are eliminated that were from var's domain.
        eliminated_function = {word: 0 for word in self.domains[var]}

        # Crossword neighbors assigned to neighbors variable.
        neighbors = self.crossword.neighbors(var)

        # Add set of neighbors in the vars domain.
        for var_word in self.domains[var]:
            # For loop, interate the vars neighbors keys.
            for neighbor in (neighbors - assignment.keys()):
                overlap = self.crossword.overlaps[var, neighbor]

                # For loop, to interate thru each given word in neighbors domain.
                for neighbor_word in self.domains[neighbor]:
                    # Increase the count on number of choices eliminated, if there is a problem.
                    # If statement, to check if the var domains and neighbors domain arent equal to each other.
                    if var_word[overlap[0]] != neighbor_word[overlap[1]]:
                        eliminated_function[var_word] += 1

        # Once counted, sort var domain in acsending order eliminate the neighbor variables.
        list_sorted = sorted(eliminated_function.items(), key=lambda x:x[1])
        return [x[0] for x in list_sorted]

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # Create a unassigned variable that will take on the assignment keys.
        unassigned_variables = self.crossword.variables - assignment.keys()

        # Remaining values in every domain.
        remaining_values = {variable: len(self.domains[variable]) for variable in unassigned_variables}
        # Sorted list of all remaining values.
        sorted_remaining_values = sorted(remaining_values.items(), key=lambda x: x[1])

        # No tie return the variable with the minimum number of remaining values.
        if len(sorted_remaining_values) == 1 or sorted_remaining_values[0][1] != sorted_remaining_values[1][1]:
            return sorted_remaining_values[0][0]

        # If statement, if there is a tie return variable with the higest degree from the domain.
        # Then sort the list from acsending order.
        else:
            highest_degrees = {variable: len(self.crossword.neighbors(variable)) for variable in unassigned_variables}
            sorted_highest_degrees = sorted (highest_degrees.items(), key=lambda x: x[1], reverse=True)
            return sorted_highest_degrees[0][0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # If statement, if the assignment of the variables is completed return None.
        if self.assignment_complete(assignment):
            return assignment

        # New variable to select the unassigned variable from assigment.
        unassigned = self.select_unassigned_variable(assignment)

        # For loop, to interate the values in the unassigned and assignment domain.
        for value in self.order_domain_values(unassigned, assignment):
            attempt = copy.deepcopy(assignment)
            attempt[unassigned] = value

            if self.consistent(attempt):
                assignment[unassigned] = value
                attempt_answer = self.backtrack(assignment)
                if attempt_answer is not None:
                    return attempt_answer

            # Finally from the assignment variable pop the unassigned and None off assignment.
            assignment.pop(unassigned, None)
        return None

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)

# Test your code!
#print("Code Completed")

if __name__ == "__main__":
    main()