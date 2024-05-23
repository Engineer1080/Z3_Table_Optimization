from z3 import IntVal, Int, z3

result = lambda p: p[0][0]
rest = lambda p: p[0][1]


class Parser:

    def parse(self, inp):
        return self.parser.parse(inp)

    def cons(x, xs):
        if type(x) == str and xs == []:
            return x
        if type(xs) == str:
            return x + xs

        return [x] + xs

    def __rshift__(self, other):
        return Seq(self, other)

    def __xor__(self, other):
        return OrElse(self, other)


####################
# Core Combinators #
####################

class ParseItem(Parser):
    """
    >>> ParseItem().parse("abc")
    [('a', 'bc')]
    >>> ParseItem().parse("")
    []
    """

    def parse(self, inp):
        if inp == "":
            return []
        return [(inp[0], inp[1:])]


class Return(Parser):
    def __init__(self, x):
        self.x = x

    def parse(self, inp):
        return [(self.x, inp)]


class Fail(Parser):
    def parse(self, inp):
        return []


class Seq(Parser):
    def __init__(self, first, and_then):
        self.first = first
        self.and_then = and_then

    def parse(self, inp):
        p = self.first.parse(inp)
        if p != []:
            return self.and_then(result(p)).parse(rest(p))
        return []


class OrElse(Parser):
    def __init__(self, parser1, parser2):
        self.parser1 = parser1
        self.parser2 = parser2

    def parse(self, inp):
        p = self.parser1.parse(inp)
        if p != []:
            return p
        return self.parser2.parse(inp)


class ParseSome(Parser):
    def __init__(self, parser):
        self.parser = parser >> (lambda x:
                                 (ParseSome(parser) ^ Return([])) >> (lambda xs:
                                                                      Return(Parser.cons(x, xs))))


class ParseIf(Parser):
    def __init__(self, pred):
        self.parser = ParseItem() >> (lambda res: Return(res) if pred(res) else Fail())


class ParseChar(Parser):
    """
    >>> ParseChar('-').parse("-89")
    [('-', '89')]
    >>> ParseChar('-').parse("89")
    []
    >>> ParseChar('a').parse("alkjdfaj")
    [('a', 'lkjdfaj')]
    >>> ParseChar('a').parse("lalkjdfaj")
    []
    """

    def __init__(self, c):
        self.parser = ParseIf(lambda s: s == c)


class ParseDigit(Parser):
    """
    >>> ParseDigit().parse("89")
    [('8', '9')]
    >>> ParseDigit().parse("-89")
    []
    """

    def __init__(self):
        self.parser = ParseIf(lambda c: c in "0123456789")


class ParseNat(Parser):
    """
    >>> ParseNat().parse("89abc")
    [(89, 'abc')]
    >>> ParseNat().parse('-89abc')
    []
    """

    def __init__(self):
        self.parser = ParseSome(ParseDigit()) >> (lambda ds: Return(int(ds)))


class ParseInt(Parser):
    """
    >>> ParseInt().parse("-89abc")
    [(-89, 'abc')]
    >>> ParseInt().parse("89ab")
    [(89, 'ab')]
    >>> ParseInt().parse("abc")
    []
    """

    def __init__(self):
        self.parser = (ParseChar('-') >> (lambda _:
                                          ParseNat() >> (lambda n:
                                                         Return(-n)))) ^ \
                      ParseNat()


class ParseSpace(Parser):
    """
    >>> ParseSpace().parse(" abc")
    [(' ', 'abc')]
    >>> ParseSpace().parse("abc")
    []
    """

    def __init__(self):
        self.parser = ParseIf(lambda c: c.isspace())


class ParseMany(Parser):
    def __init__(self, parser):
        self.parser = ParseSome(parser) ^ Return([])


class ParseToken(Parser):
    def __init__(self, parser):
        self.parser = ParseMany(ParseSpace()) >> (lambda _:
                                                  parser >> (lambda x:
                                                             ParseMany(ParseSpace()) >> (lambda _:
                                                                                         Return(x))))


class ParseNumber(Parser):
    def __init__(self):
        self.parser = ParseToken(ParseInt())


class ParseIdent(Parser):
    """
    >>> ParseIdent().parse("abc")
    [('abc', '')]
    >>> ParseIdent().parse("a bc")
    [('a', ' bc')]
    """

    def __init__(self):
        self.parser = ParseIf(lambda c: c.isalpha()) >> (lambda c:
                                                         ParseMany(ParseIf(lambda c: c.isalnum())) >> (lambda cs:
                                                                                                       Return(
                                                                                                           Parser.cons(
                                                                                                               c, cs))))


class ParseIdentifier(Parser):
    def __init__(self):
        self.parser = ParseToken(ParseIdent())


"""
<table> ::= <dimension> <constraints>
<dimension> ::= <number> , <number> ;
<number> ::= <digit> | <digit> <number> | <digit>0<number> | <digit>0 
<digit> ::= 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 
<constraints> ::= <tableexpression> <comparison> <tableexpression> ;
<tableexpression> ::= <int> | <reference> | <addition> | <substraction> | <multiplication> | (<tableexpression>)
<addition> ::= <tableexpression> + <tableexpression>
<substraction> ::= <tableexpression> - <tableexpression>
<multiplication> ::= <tableexpression> * <tableexpression>
<reference> ::= A<expr><expr>
<expr> ::= <int> | <var> | (<expr>) | <expr> + <expr> | <expr> * <expr>
<int> ::= <number> | 0 | -<number> 
<comparison> ::= < | <= | = | >= | >
"""


class Dimension:
    def __init__(self, first, second):
        self.first = first
        self.second = second

    def __repr__(self):
        return f'Dimension({self.first}, {self.second})'


class ParseDimension(
    Parser):  # Hier wird die Dimension geparst durch die ParserCombinators (ParseNumber, ParseChar) und das semicolon wird "entfehrnt"
    """
    >>> ParseDimension().parse("4 , 10 ;")
    [(Dimension(4, 10), '')]
    >>> ParseDimension().parse("01 , 3   ;")
    [(Dimension(1, 3), '')]
    >>> ParseDimension().parse("2, 2 ;")
    [(Dimension(2, 2), '')]
    """

    def __init__(self):
        self.parser = (ParseNumber() >> (lambda x:
                                         ParseChar(',') >> (lambda _:
                                                            ParseNumber() >> (lambda y:
                                                                              ParseToken(ParseChar(';')) >> (lambda _:
                                                                                                             Return(
                                                                                                                 Dimension(
                                                                                                                     x,
                                                                                                                     y))))))
                       ) ^ ParseNumber()


class Con:
    def __init__(self, con):
        self.con = con

    def __repr__(self):
        return f'Con({self.con})'

    def to_z3(self):
        return IntVal(self.con)

    def to_z3_new(self):
        return IntVal(self.con)


class Var:
    def __init__(self, var):
        self.var = var

    def __repr__(self):
        return f'Var({self.var})'

    def to_z3(self):
        return Int(self.var)

    def to_z3_new(self):
        return Int(self.var)


class ParseExpr(Parser):  # Dieser Parser unterscheidet zwischen Con durch ParseNumber oder Var durch ParseIdentifier
    def __init__(self):
        """
        >>> ParseExpr().parse("123 abc")
        [(Con(123), 'abc')]
        >>> ParseExpr().parse("abc 123")
        [(Var(abc), '123')]

        """
        self.parser = (ParseNumber() >> (lambda x: Return(Con(x)))) ^ \
                      (ParseIdentifier() >> (lambda name: Return(Var(name))))


class Times:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f'Times({self.x}, {self.y})'

    def to_z3(self):
        return f'{self.x.to_z3()} * {self.y.to_z3()}'

    def to_z3_new(self):
        return self.x.to_z3_new() * self.y.to_z3_new()


class ParseMultiply(
    Parser):  # Hier wird das * zeichen innerhalb der Matrix-Klammern geparst bzw auch die dazugehörigen expressions mit ParseExpr
    """
    >>> ParseMultiply().parse("12 * 3 abc")
    [(Times(Con(12), Con(3)), 'abc')]
    >>> ParseMultiply().parse("12 * x abc")
    [(Times(Con(12), Var(x)), 'abc')]
    """

    def __init__(self):
        self.parser = (ParseExpr() >> (lambda x:
                                       ParseChar('*') >> (lambda _:
                                                          ParseMultiply() >> (lambda y:
                                                                              Return(Times(x, y)))))) ^ ParseExpr()


class Plus:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f'Plus({self.x}, {self.y})'

    def to_z3(self):
        return f'{self.x.to_z3()} + {self.y.to_z3()}'

    def to_z3_new(self):
        return self.x.to_z3_new() + self.y.to_z3_new()


class ParseAdd(Parser):  # hier wird das + zeichen geparst und ParseMultiply verwendet
    """
    >>> ParseAdd().parse("123 + 125 * 71 +  10 abc")
    [(Plus(Con(123), Plus(Times(Con(125), Con(71)), Con(10))), 'abc')]
    >>> ParseAdd().parse("123 + 125 * 71 +  10 * abc")
    [(Plus(Con(123), Plus(Times(Con(125), Con(71)), Times(Con(10), Var(abc)))), '')]
    """

    def __init__(self):
        self.parser = (ParseMultiply() >> (lambda x:
                                           ParseChar('+') >> (lambda _:
                                                              ParseAdd() >> (lambda y:
                                                                             Return(Plus(x, y)))))) ^ ParseMultiply()


class Matrix:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # self.matrix = matrix

    def __repr__(self):
        return f'Matrix({self.x}, {self.y})'

    def to_z3(self):
        return f'A[{self.x.to_z3()}][{self.y.to_z3()}]'

    # def to_z3_new(self):
    # return self.matrix[self.x.to_z3_new()][self.y.to_z3_new()]


class ParseBrackets(Parser):  # hier werden die [] zeichen geparst und durch das ParseAdd auch der inhalt der klammern
    """
    >>> ParseBrackets().parse("[3] abc")
    [(Con(3), 'abc')]
    >>> ParseBrackets().parse("[1 + a] anc")
    [(Plus(Con(1), Var(a)), 'anc')]
    """

    def __init__(self):
        self.parser = (ParseToken(ParseChar('[')) >> (lambda _:
                                                      ParseAdd() >> (lambda x:
                                                                     ParseToken(ParseChar(']')) >> (lambda _:
                                                                                                    Return(x)))))


class ParseMatrix(
    Parser):  # Hier wird die Matrix geparsed, hier wird zunächst das A entfehrnt und anschließend werden beide Klammern geparsd durch ParseBrackets
    """
    >>> ParseMatrix().parse("A[2][1] abc")
    [(Matrix(Con(2), Con(1)), 'abc')]
    >>> ParseMatrix().parse("A[i][j] abc")
    [(Matrix(Var(i), Var(j)), 'abc')]
    """

    def __init__(self):
        self.parser = (ParseChar('A') >> (lambda _:
                                          ParseBrackets() >> (lambda x:
                                                              ParseBrackets() >> (lambda y:
                                                                                  Return(Matrix(x, y))))))


class Smaller:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f'Smaller({self.x}, {self.y})'

    def to_z3(self):
        return f'{self.x.to_z3()} < {self.y.to_z3()}'

    def to_z3_new(self):
        return self.x.to_z3_new() < self.y.to_z3_new()


class Bigger:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f'Bigger({self.x}, {self.y})'

    def to_z3(self):
        return f'{self.x.to_z3()} > {self.y.to_z3()}'

    def to_z3_new(self):
        return self.x.to_z3_new() > self.y.to_z3_new()


class SmallerEqual:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f'SmallerEqual({self.x}, {self.y})'

    def to_z3(self):
        return f'({self.x.to_z3()} <= {self.y.to_z3()})'

    def to_z3_new(self):
        return self.x.to_z3_new() <= self.y.to_z3_new()


class BiggerEqual:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f'BiggerEqual({self.x}, {self.y})'

    def to_z3(self):
        return f'{self.x.to_z3()} >= {self.y.to_z3()}'

    def to_z3_new(self):
        return self.x.to_z3_new() >= self.y.to_z3_new()


class Equal:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f'Equal({self.x}, {self.y})'

    def to_z3(self):
        return f'{self.x.to_z3()} == {self.y.to_z3()}'

    def to_z3_new(self):
        return self.x.to_z3_new() == self.y.to_z3_new()


class ParseEqual(Parser):  # Parsed das = zeichen und ruft ParseAddTable auf
    """
    >>> ParseEqual().parse("A[1][2] = A[x][a] abc")
    [(Equal(Matrix(Con(1), Con(2)), Matrix(Var(x), Var(a))), 'abc')]
    >>> ParseEqual().parse("A[1][2] = 2 abc")
    [(Equal(Matrix(Con(1), Con(2)), Con(2)), 'abc')]
    >>> ParseEqual().parse("x = A[x][a] abc")
    [(Equal(Var(x), Matrix(Var(x), Var(a))), 'abc')]
    """

    def __init__(self):
        self.parser = (ParseAddTable() >> (lambda x:
                                           ParseToken(ParseChar('=')) >> (lambda _:
                                                                          ParseEqual() >> (lambda y:
                                                                                           Return(Equal(x,
                                                                                                        y)))))) ^ ParseAddTable()


class ParseLessEqual(Parser):  # Hilfsklasse für ParseSmallerEqual
    def __init__(self):
        self.parser = (ParseToken(ParseChar('<')) >> (lambda _:
                                                      ParseToken(ParseChar('=')) >> (lambda _:
                                                                                     Return(self))))


class ParseMoreEqual(Parser):  # Hilfsklasse für ParseBiggerEqual
    def __init__(self):
        self.parser = (ParseToken(ParseChar('>')) >> (lambda _:
                                                      ParseToken(ParseChar('=')) >> (lambda _:
                                                                                     Return(self))))


class ParseSmallerEqual(
    Parser):  # Parsed das <= zeichen und ruft ParseEqual auf besonderheit: das zeichen wird in der classe ParseLessEqual geparsed
    """
    >>> ParseSmallerEqual().parse("A[1][2] <= A[x][a] abc")
    [(SmallerEqual(Matrix(Con(1), Con(2)), Matrix(Var(x), Var(a))), 'abc')]
    >>> ParseSmallerEqual().parse("A[1][2] <= 2 abc")
    [(SmallerEqual(Matrix(Con(1), Con(2)), Con(2)), 'abc')]
    >>> ParseSmallerEqual().parse("x <= A[x][a] abc")
    [(SmallerEqual(Var(x), Matrix(Var(x), Var(a))), 'abc')]
    >>> ParseSmallerEqual().parse("A[i][j] <= 10")
    [(SmallerEqual(Matrix(Var(i), Var(j)), Con(10)), '')]
    """

    def __init__(self):
        self.parser = (ParseEqual() >> (lambda x:
                                        ParseLessEqual() >> (lambda _:
                                                             ParseSmallerEqual() >> (lambda y:
                                                                                     Return(SmallerEqual(x,
                                                                                                         y)))))) ^ ParseEqual()


class ParseBiggerEqual(
    Parser):  # Parsed das >= zeichen und ruft ParseSmallerEqual auf besonderheit: das zeichen wird in der classe ParseMoreEqual geparsed
    """
    >>> ParseBiggerEqual().parse("A[1][2] >= A[x][a] abc")
    [(BiggerEqual(Matrix(Con(1), Con(2)), Matrix(Var(x), Var(a))), 'abc')]
    >>> ParseBiggerEqual().parse("A[1][2] >= 2 abc")
    [(BiggerEqual(Matrix(Con(1), Con(2)), Con(2)), 'abc')]
    >>> ParseBiggerEqual().parse("x >= A[x][a] abc")
    [(BiggerEqual(Var(x), Matrix(Var(x), Var(a))), 'abc')]
    """

    def __init__(self):
        self.parser = (ParseSmallerEqual() >> (lambda x:
                                               ParseMoreEqual() >> (lambda _:
                                                                    ParseBiggerEqual() >> (lambda y:
                                                                                           Return(BiggerEqual(x,
                                                                                                              y)))))) ^ ParseSmallerEqual()


class ParseBigger(Parser):  # Parsed das > zeichen und ruft ParseBiggerEqual auf
    """
    >>> ParseBigger().parse("A[1][2] > A[x][a] abc")
    [(Bigger(Matrix(Con(1), Con(2)), Matrix(Var(x), Var(a))), 'abc')]
    >>> ParseBigger().parse("A[1][2] > 2 abc")
    [(Bigger(Matrix(Con(1), Con(2)), Con(2)), 'abc')]
    >>> ParseBigger().parse("x > A[x][a] abc")
    [(Bigger(Var(x), Matrix(Var(x), Var(a))), 'abc')]
    """

    def __init__(self):
        self.parser = (ParseBiggerEqual() >> (lambda x:
                                              ParseToken(ParseChar('>')) >> (lambda _:
                                                                             ParseBigger() >> (lambda y:
                                                                                               Return(Bigger(x,
                                                                                                             y)))))) ^ ParseBiggerEqual()


class ParseSmaller(Parser):  # Wird benutzt um das < zeichen zu parsen und ruft ParseBigger auf
    """
    >>> ParseSmaller().parse("A[1][2] < A[x][a] abc")
    [(Smaller(Matrix(Con(1), Con(2)), Matrix(Var(x), Var(a))), 'abc')]
    >>> ParseSmaller().parse("A[1][2] < 2 abc")
    [(Smaller(Matrix(Con(1), Con(2)), Con(2)), 'abc')]
    >>> ParseSmaller().parse("x < A[x][a] abc")
    [(Smaller(Var(x), Matrix(Var(x), Var(a))), 'abc')]
    """

    def __init__(self):
        self.parser = (ParseBigger() >> (lambda x:
                                         ParseToken(ParseChar('<')) >> (lambda _:
                                                                        ParseSmaller() >> (lambda y:
                                                                                           Return(Smaller(x,
                                                                                                          y)))))) ^ ParseBigger()


class ParseMatrixOrNumber(
    Parser):  # Wird benutzt um ParseMatrix oder ParseNumber oder ParseIdentifier oder ParseSpace auszuführen
    """
    >>> ParseMatrixOrNumber().parse("A[1][a] abc")
    [(Matrix(Con(1), Var(a)), 'abc')]
    >>> ParseMatrixOrNumber().parse("21 abc")
    [(Con(21), 'abc')]
    """

    def __init__(self):
        self.parser = (ParseMatrix() >> (lambda x: Return(x))) ^ \
                      (ParseNumber() >> (lambda x: Return(Con(x)))) ^ \
                      (ParseIdentifier() >> (lambda x: Return(Var(x)))) ^ \
                      (ParseSpace())


class ParseCompare(
    Parser):  # Diese klasse ruft eigentlich nur ParseSmaller auf. Es ist redundant aber dadurch besser verständlich auch für die tests
    """
    >>> ParseCompare().parse("A[1][2] < 2 abc")
    [(Smaller(Matrix(Con(1), Con(2)), Con(2)), 'abc')]
    >>> ParseCompare().parse("A[1][2] > A[x][a] abc")
    [(Bigger(Matrix(Con(1), Con(2)), Matrix(Var(x), Var(a))), 'abc')]
    >>> ParseCompare().parse("A[1][2] >= A[x][a] abc")
    [(BiggerEqual(Matrix(Con(1), Con(2)), Matrix(Var(x), Var(a))), 'abc')]
    >>> ParseCompare().parse("A[1][2] <= A[x][a] abc")
    [(SmallerEqual(Matrix(Con(1), Con(2)), Matrix(Var(x), Var(a))), 'abc')]
    >>> ParseCompare().parse("A[1][2] = A[x][a] abc")
    [(Equal(Matrix(Con(1), Con(2)), Matrix(Var(x), Var(a))), 'abc')]
    """

    def __init__(self):
        self.parser = (ParseSmaller())


class Parenthesis:
    def __init__(self, x):
        self.x = x

    def __repr__(self):
        return f'Parenthesis({self.x})'

    def to_z3(self):
        return f'({self.x.to_z3()})'

    def to_z3_new(self):
        return self.x.to_z3_new()


class Sub:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f'Sub({self.x}, {self.y})'

    def to_z3(self):
        return f'{self.x.to_z3()} - {self.y.to_z3()}'

    def to_z3_new(self):
        return self.x.to_z3_new() - self.y.to_z3_new()


class ParseSub(Parser):  # parst das - zeichen und führt ParseMultiplyTable aus
    """
    >>> ParseSub().parse("A[1][2] - 3 abc")
    [(Sub(Matrix(Con(1), Con(2)), Con(3)), 'abc')]
    >>> ParseSub().parse("A[1][2] * A[a][b] - 2 abc")
    [(Sub(Times(Matrix(Con(1), Con(2)), Matrix(Var(a), Var(b))), Con(2)), 'abc')]
    """

    def __init__(self):
        self.parser = (ParseMultiplyTable() >> (lambda x:
                                                ParseToken(ParseChar('-')) >> (lambda _:
                                                                               ParseSub() >> (lambda y:
                                                                                              Return(
                                                                                                  Sub(x,
                                                                                                      y)))))) ^ ParseMultiplyTable()


class ParseMultiplyTable(
    Parser):  # hier wird das * zeichen geparst außerdem führt er ParseMatrixOrNumber aus hier ist eine besonderheit zu beachten, es wird auch für die aufrufe von ParseParenthesis benutzt
    """
    >>> ParseMultiplyTable().parse("A[1][2] * 3 abc")
    [(Times(Matrix(Con(1), Con(2)), Con(3)), 'abc')]
    >>> ParseMultiplyTable().parse("A[1][2] * A[1][2] abc")
    [(Times(Matrix(Con(1), Con(2)), Matrix(Con(1), Con(2))), 'abc')]
    >>> ParseMultiplyTable().parse("(A[1][2] * A[a][b] + 2) as")
    [(Parenthesis(Plus(Times(Matrix(Con(1), Con(2)), Matrix(Var(a), Var(b))), Con(2))), 'as')]
    """

    def __init__(self):
        self.parser = (ParseMatrixOrNumber() >> (lambda x:
                                                 ParseToken(ParseChar('*')) >> (lambda _:
                                                                                ParseMultiplyTable() >> (lambda y:
                                                                                                         Return(Times(x,
                                                                                                                      y)))))) ^ ParseMatrixOrNumber() ^ \
                      (ParseParenthesis() >> (lambda x:
                                              ParseToken(ParseChar('*')) >> (lambda _:
                                                                             ParseMultiplyTable() >> (lambda y:
                                                                                                      Return(Times(x,
                                                                                                                   y)))))) ^ \
                      (ParseParenthesis())


class ParseAddTable(Parser):  # parst das + zeichen und führt ParseSub aus
    """
    >>> ParseAddTable().parse("A[1][2] * 3 + 4 abc")
    [(Plus(Times(Matrix(Con(1), Con(2)), Con(3)), Con(4)), 'abc')]
    >>> ParseAddTable().parse("A[1][2] * A[a][b] + 2 abc")
    [(Plus(Times(Matrix(Con(1), Con(2)), Matrix(Var(a), Var(b))), Con(2)), 'abc')]
    >>> ParseAddTable().parse("A[1][2] * A[a][b] - 2 abc")
    [(Sub(Times(Matrix(Con(1), Con(2)), Matrix(Var(a), Var(b))), Con(2)), 'abc')]
    >>> ParseAddTable().parse("A[1][2] * A[a][b] - 2 - ( A[a][v] - 5 ) abc")
    [(Sub(Times(Matrix(Con(1), Con(2)), Matrix(Var(a), Var(b))), Sub(Con(2), Parenthesis(Sub(Matrix(Var(a), Var(v)), Con(5))))), 'abc')]
    >>> ParseAddTable().parse("( A[a][v] - 5 ) * ( A[a][v] + 5 )")
    [(Times(Parenthesis(Sub(Matrix(Var(a), Var(v)), Con(5))), Parenthesis(Plus(Matrix(Var(a), Var(v)), Con(5)))), '')]
    """

    def __init__(self):
        self.parser = (ParseSub() >> (lambda x:
                                      ParseToken(ParseChar('+')) >> (lambda _:
                                                                     ParseAddTable() >> (lambda y:
                                                                                         Return(
                                                                                             Plus(x,
                                                                                                  y)))))) ^ ParseSub()


class ParseParenthesis(Parser):  # Parst die klammern
    """
    >>> ParseParenthesis().parse("(A[1][2] * A[a][b] + 2) as")
    [(Parenthesis(Plus(Times(Matrix(Con(1), Con(2)), Matrix(Var(a), Var(b))), Con(2))), 'as')]
    """

    def __init__(self):
        self.parser = (ParseToken(ParseChar('(')) >> (lambda _:
                                                      ParseAddTable() >> (lambda x:
                                                                          ParseToken(ParseChar(')')) >> (lambda _:
                                                                                                         Return(
                                                                                                             Parenthesis(
                                                                                                                 x))))))


class ParseFullCondition(
    Parser):  # ParseFullConditions ruft parsecompare auf und entfehrnt das übrigbleibende semicolon
    """
    >>> ParseFullCondition().parse("(A[i][j] - A[i][j+1])*(A[i][j] - A[i][j+1]);")
    [(Times(Parenthesis(Sub(Matrix(Var(i), Var(j)), Matrix(Var(i), Plus(Var(j), Con(1))))), Parenthesis(Sub(Matrix(Var(i), Var(j)), Matrix(Var(i), Plus(Var(j), Con(1)))))), '')]
    >>> ParseFullCondition().parse("A[i][j] <= 10;")
    [(SmallerEqual(Matrix(Var(i), Var(j)), Con(10)), '')]
    >>> ParseFullCondition().parse("A[i][j] > -5;")
    [(Bigger(Matrix(Var(i), Var(j)), Con(-5)), '')]
    >>> ParseFullCondition().parse("A[1][j] + A[2][j] > 1;")
    [(Bigger(Plus(Matrix(Con(1), Var(j)), Matrix(Con(2), Var(j))), Con(1)), '')]
    >>> ParseFullCondition().parse("A[i][j] < A[i+1][j];")
    [(Smaller(Matrix(Var(i), Var(j)), Matrix(Plus(Var(i), Con(1)), Var(j))), '')]
    >>> ParseFullCondition().parse("A[i][j] >= 1;")
    [(BiggerEqual(Matrix(Var(i), Var(j)), Con(1)), '')]
    >>> ParseFullCondition().parse("A[i][j] <= 10;")
    [(SmallerEqual(Matrix(Var(i), Var(j)), Con(10)), '')]
    >>> ParseFullCondition().parse("A[i][j] = A[j][i];")
    [(Equal(Matrix(Var(i), Var(j)), Matrix(Var(j), Var(i))), '')]
    >>> ParseFullCondition().parse("A[i][j] >= 1;")
    [(BiggerEqual(Matrix(Var(i), Var(j)), Con(1)), '')]
    >>> ParseFullCondition().parse("A[i][j] <= 10;")
    [(SmallerEqual(Matrix(Var(i), Var(j)), Con(10)), '')]
    >>> ParseFullCondition().parse("A[i][j] = A[j][i];")
    [(Equal(Matrix(Var(i), Var(j)), Matrix(Var(j), Var(i))), '')]
    >>> ParseFullCondition().parse("A[i][i+k] < A[i][i+k+1];")
    [(Smaller(Matrix(Var(i), Plus(Var(i), Var(k))), Matrix(Var(i), Plus(Var(i), Plus(Var(k), Con(1))))), '')]
    >>> ParseFullCondition().parse("A[i][j] > 0;")
    [(Bigger(Matrix(Var(i), Var(j)), Con(0)), '')]
    >>> ParseFullCondition().parse("A[2][2] = 3;")
    [(Equal(Matrix(Con(2), Con(2)), Con(3)), '')]
    >>> ParseFullCondition().parse("(A[i][j] - A[i+1][j])*(A[i][j] - A[i+1][j]) >= 1 ;")
    [(BiggerEqual(Times(Parenthesis(Sub(Matrix(Var(i), Var(j)), Matrix(Plus(Var(i), Con(1)), Var(j)))), Parenthesis(Sub(Matrix(Var(i), Var(j)), Matrix(Plus(Var(i), Con(1)), Var(j))))), Con(1)), '')]
    >>> ParseFullCondition().parse("(A[i][j] - A[i][j+1])*(A[i][j] - A[i][j+1]) >= 1;")
    [(BiggerEqual(Times(Parenthesis(Sub(Matrix(Var(i), Var(j)), Matrix(Var(i), Plus(Var(j), Con(1))))), Parenthesis(Sub(Matrix(Var(i), Var(j)), Matrix(Var(i), Plus(Var(j), Con(1)))))), Con(1)), '')]
    """

    def __init__(self):
        self.parser = (ParseCompare() >> (lambda x:
                                          ParseToken(ParseChar(';')) >> (lambda _:
                                                                         Return(x))))


class StartToParse:  # StartToParse wird verwendet um die Textdatei einzulesen, die erste Zeile zu benutzen für die Dimensionsbestimmung und die restlichen als conditions zu parsen
    def start(self, filename):
        """>>> StartToParse().start(filename) #Die Tests hier werden Fehlschlagen bei einer anderen Textdatei
        Dimension(3, 3)
        Bigger(Matrix(Var(i), Var(j)), Con(0))
        Equal(Matrix(Con(2), Con(2)), Con(3))
        BiggerEqual(Times(Parenthesis(Sub(Matrix(Var(i), Var(j)), Matrix(Plus(Var(i), Con(1)), Var(j)))), Parenthesis(Sub(Matrix(Var(i), Var(j)), Matrix(Plus(Var(i), Con(1)), Var(j))))), Con(1))
        BiggerEqual(Times(Parenthesis(Sub(Matrix(Var(i), Var(j)), Matrix(Var(i), Plus(Var(j), Con(1))))), Parenthesis(Sub(Matrix(Var(i), Var(j)), Matrix(Var(i), Plus(Var(j), Con(1)))))), Con(1))
        """
        with open(filename, 'r') as file:  # Hier ändern des Namens der Textdatei
            lines = []
            for line in file:
                line = line.strip()
                lines.append(line)
            parsed = []
            for x in range(0, len(lines)):
                if x == 0:
                    parsed.append(ParseDimension().parse(lines[x]))
                    global Dimensions
                    Dimensions = ParseDimension().parse(lines[x])[0][0]
                else:
                    parsed.append(ParseFullCondition().parse(lines[x]))
                    global AllConditions
                    AllConditions.append(ParseFullCondition().parse(lines[x])[0][0])

            # for x in range(0, len(parsed)):
            # if parsed[x][0][1] == '':  # Hier wird überprüft ob der Parser die komplette Zeile parsen konnte
            # print(parsed[x][0][0])
            # else:  # falls etwas nicht fertig geparst wurde printed er ein Error
            #print("ERROR")


Dimensions = Dimension(0, 0)  # Globale Variable, hier wird die Dimension gespeichert nach dem Parsen
AllConditions = []  # Globaler Array, hier wird Zeile für Zeile der geparseten Bedingungen abgespeichert
