# Z3_Table_Optimization

Project Description
The aim of this project is to solve a simplified version of a very common problem, instances of which appear in
scheduling, production planning, resource allocation, etc. The problem is to find integer values with which to fill
an m × n table, ensuring that given constraints on the values are met, and in such a way that the sum of the
values in the table is minimal.
For example, fill in a 2 × 3 table A such that
• A[i][j] ≤ 10
• A[i][j] > −5
• A[1][j] + A[2][j] > 1
• A[i][j] < A[i + 1][j]
Variables that appear as indices are assumed to be universally bound, i.e., the condition must hold for all indices
in the range of the table. The first index is the row index, ranging from 1 to m, the second is the column index,
ranging from 1 to n. Thus, the last condition is an abbreviation for the list
• A[1][1] < A[2][1]
• A[1][2] < A[2][2]
• A[1][3] < A[2][3]
A table satisfying these constraints is
−3 2 −1
10 4 3
This is, however, not a minimal-sum solution. An actual minimal sum solution to this problem is, for example:
−4 −2 0
6 4 2
(the third constraint tells us that the sum of all values will be ≥ 6). The minimal solution is, in general, not unique.
You should implement a solve function that takes as argument a filename in which the problem description is
stored. The solution is given as a list of lists. For example, the above solution would be returned as
 tbl = solve(”tbldsc.txt”)
 tbl
[[-4, -2, 0], [6, 4, 2]]
It can happen that a problem has no solution. For example
2, 3;
A[i][j] > 0 ;
A[1][1] + A[1][2] = 0 ;
1
is such a problem. The function solve should in such a case return the empty list and print a message:
 tbl = solve(”impossible.txt”)
No solution found!
 tbl
[]
Table Constraints
Table constraints are equalities and inequalities between symbolic expressions involving references of the form
A[i][j].
Index Expressions
Index expressions (expressions used in the square brackets to create references to table locations) are either
integer constants, variables, or arithmetical expressions involving addition and multiplication (no subtraction or
division etc.).
Examples are: 1, x, 2 ∗ i + 2, i + k, j ∗ j, 2 ∗ (i + j), i ∗ (x + 1).
Table References
Table references have the form A[row expression][column expression], where the row and column expressions
are index expressions.
Examples: A[i][x], A[2][3 ∗ i + 1], A[j][i]
Table Expressions
Table expressions are built from integer constants, table references, addition, subtraction and multiplication.
Examples of table expressions:
42
A[1][2]
A[i][j] + 2*A[2][j]
15 + A[1][2]*A[1][2]
(A[1][2] - 2) - A[i][j]
All operations are assumed to associate to the right (so x - y - z would result in x - (y - z)).
Table Constraints
Table constraints are comparisons between two table expressions, the allowed comparisons being <, <=, =, >=, >.
Examples:
A[i][j] = A[j][i]
A[1][i] < A[2][j]
A[i][i + k] >= 10
A[1][2] + A[i][j] >= 3 * A[2][2]
(A[1][1] - A[2][1])*(A[2][2] - A[1][2]) <= A[i][j]
2
When free variables appear in the indices, they are assumed to be universally quantified over the range of allowed
values. All variables are strictly positive. For example, if m = 2 and n = 4, the first in the above examples is
interpreted as
∀i ∈ {1, 2} ∀j ∈ {1, 2} A[i][j] = A[j][i]
equivalent to the list of constraints
A[1][1] = A[1][1]
A[1][2] = A[2][1]
A[2][1] = A[1][2]
A[2][2] = A[2][2]
The ranges of i and j are constrained by their use both as row and as column indices.
The second constraint should be interpreted as
∀i ∈ {1, 2, 3, 4} ∀j ∈ {1, 2, 3, 4} A[1][i] < A[2][j]
equivalent to the list of constraints
A[1][1] < A[2][1]
A[1][1] < A[2][2]
A[1][1] < A[2][3]
A[1][1] < A[2][4]
A[1][2] < A[2][1]
A[1][2] < A[2][2]
A[1][2] < A[2][3]
A[1][2] < A[2][4]
The third example would be interpreted as
∀i ∈ {1, 2} ∀k ∈ {k | 1 ≤ i + k ≤ 4, k ≥ 1} A[i][i + k] >= 10
equivalent to the list of constraints
A[1][2] >= 10
A[1][3] >= 10
A[1][4] >= 10
A[2][3] >= 10
A[2][4] >= 10
Table Specification
The solve function reads the table specification from a file that must have the following format:
• it starts with the table dimensions, two strictly positive natural numbers, separated by a comma and followed by a semicolon: m, n;
• a number of table constraints separated by semicolons.
Examples:
• The first example above:
2, 3 ;
A[i][j] <= 10;
A[i][j] > -5 ;
A[1][j] + A[2][j] > 1 ;
A[i][j] < A[i+1][j] ;
• A symmetric 4 by 4 table of values between 1 and 10 inclusive:
3
4, 4;
A[i][j] >= 1 ;
A[i][j] <= 10 ;
A[i][j] = A[j][i] ;
The minimal solution is: all values equal to 1.
• A symmetric 4 by 4 table of values between 1 and 10 inclusive, such that the values on the right of the
diagonal are in increasing order in each row:
4, 4;
A[i][j] >= 1 ;
A[i][j] <= 10 ;
A[i][j] = A[j][i] ;
A[i][i+k] < A[i][i+k+1] ;
The minimal solution is:
1 2 3 4
2 1 2 3
3 2 1 2
4 3 2 1
• A 3 by 3 table of strictly positive values, containing a 3 in the centre, such that no neighbouring values are
closer together than 1:
3, 3 ;
A[i][j] > 0 ;
A[2][2] = 3 ;
(A[i][j] - A[i+1][j])*(A[i][j] - A[i+1][j]) >= 1 ;
(A[i][j] - A[i][j+1])*(A[i][j] - A[i][j+1]) >= 1 ;
A minimal solution is:
2 1 2
1 3 1
2 1 2

The project consists of several parts:
• a BNF grammar for table specifications (dimensions and constraints)
• classes for representing table specifications (including index expressions, table references, table expressions and constraints)
• a parser for table specifications
• a method of translating table specification to Z3 constraints
• an application of Z3 to determining the values A[i][j].
