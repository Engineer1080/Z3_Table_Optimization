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
>>> tbl = solve(”tbldsc.txt”)
>>> tbl
[[-4, -2, 0], [6, 4, 2]]
It can happen that a problem has no solution. For example
2, 3;
A[i][j] > 0 ;
A[1][1] + A[1][2] = 0 ;
1
is such a problem. The function solve should in such a case return the empty list and print a message:
>>> tbl = solve(”impossible.txt”)
No solution found!
>>> tbl
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
A Grammar of Table Specifications
The first task is to create a BNF grammar for the table specifications, based on the description given above and
on the examples. You may use any “reasonable” BNF-variant that you wish: EBNF, BNFC, Russell-Norvig style,
etc.
Note: The examples given above are expected to parse without errors!
Implementing Table Constraints
The next task is to implement classes for representing the index expressions, table references, table expressions,
and table constraints. Feel free to reuse code we implemented in the course, but avoid bringing in dead code
(e.g., there is no use here for differentiation!).
Parsing
The result of parsing a problem description should be a table specification: the table dimensions and the table
constraints. I recommend using our parser combinators to implement the parsing, but you are allowed to use
other methods as well. However, other methods will be graded “all or none”: full marks if the parsing works
perfectly, otherwise zero! Note: mixing a bit of parser combinators with a lot of Python regular expressions
counts as “other methods”.
4
Using the Z3 Solver
The heavy-lifting of actually filling in the table should be left to the Z3 solver. In order to achieve this, you should
translate the parsed table constraints to Z3 constraints. You could achieve this by adding a toZ3 method to the
various classes (similar in many ways to the evaluation method). This method would translate an arithmetic or
boolean expression to a corresponding Z3 expression.
Summary and Assessment
The project consists of several parts:
• a BNF grammar for table specifications (dimensions and constraints)
• classes for representing table specifications (including index expressions, table references, table expressions and constraints)
• a parser for table specifications
• a method of translating table specification to Z3 constraints
• an application of Z3 to determining the values A[i][j].
The project must be completed in pairs (or individually). I recommend splitting the work along the parsing/Z3
divide, working together on the grammar and designing the classes. This way, the bulk of the implementation
can be parallelized, since Z3 doesn’t connect directly to the parser.
Each submission must be accompanied by two documents, each one to two pages long:
• a joint description of the grammar and the design of the classes that implement the table specifications,
and of the code that was produced jointly
• an individual paper containing
– a clear identification of the parts for which they were responsible
– a brief description of their code (e.g., the parsing, or the toZ3 methods, etc.)
– additional remarks that can help the reader understand and use the code
– a list of any deviations from the specification that you needed to make
– potential extensions that could be made to the code, or alternative designs or implementations
– a list of bugs that you are aware of.
In brief, the description should summarize the information you would communicate in an oral presentation in front
of a code review team.
The final grade will be computed from a weighted average of marks awarded for code correctness, clarity, consistency, and efficiency, and the marks awarded for the description.
Please note:
• You may collaborate freely on the code and the joint document with your team partner, but not on the
individual paper. No collaboration is permitted outside the team.
• Each participant must submit an archive (zip, rar, tar, tgz, etc.) containing:
– a README file with the name and matriculation number of the participant, and the name of the other
team member
– the work description (both joint and individual) in plain text or pdf format (not doc, docx, odt, rtf,
html, …) Markdown formats are acceptable, as long as they are contained in plain text files,
– the code produced by the team.
5
Thus, both participants will submit the entire code and the joint work description, and each participant
submits their own individual paper.
The archive must be uploaded to iLearn by the specified deadline. Solutions sent to me by email will
not be considered!
• You may use any code we implemented in the course, but you must only include what is necessary for
the assignment (e.g., no code for differentiation of symbolic expressions!)
• Follow the specification to the letter! Do not, for example, use : instead of ;, or call the table references
B[i][j] instead of A[i][j], or introduce extra punctuation to separate constraints, etc. The function
solve must have exactly this name, and it should take an arbitrary string as file name. Do not hardcode
filenames or extensions! This could very well lead to failing the project for both team members.
• You may assume that the input file is well formed, i.e.
– there are no dangling parentheses or missing semicolons,
– there are no subtractions or other operations in index expressions, and no operations other than +, -,
* in table expressions,
– there are no other comparisons between table expressions other than <, <= etc.
– there are no non-integer numbers, etc.
Therefore, you do not need to check for such errors in input. However, make sure you do not parse ungrammatical inputs! For example, 2, 2 ; 2, 3 ; should fail, because the table specification may only contain
one m, n pair (which has to be the first thing in the file). The resulting parse is empty and the program is
allowed to crash because of “user error”. If you do parse this erroneous input and even return a solution,
then points will be deducted!
• Code must be commented to help the reader understand what is going on and explain design decisions
not listed in the work description. You should include testable examples in docstrings, at least for the main
functions (such as solve).
In general, you are strongly encouraged to test your project before submitting it! In the past, a surprisingly
large number of submissions contained errors that would have easily been caught by a reasonable testing
process.
• The only acceptable format for Python code is plain *.py scripts! Jupyter notebooks and other formats
will not be taken into account under any circumstances!
Make sure that your code is legible and aim for clarity and consistency (which are more important in this
context than efficiency). Be aware that tools that automatically extract tools from notebooks often leave
the code in a messy state. Submitting such code will lead to significant point deductions!
Failure to observe these points will likely lead to a failing mark on this project!
