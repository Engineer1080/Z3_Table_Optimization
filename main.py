import z3
import myparser
from myparser import AllConditions, StartToParse


def solve(filename):
    StartToParse().start(filename)
    with open(filename, 'r') as file:
        # Auslesen der ersten Zeile der Datei und Leerzeichen entfernen
        first_line = file.readline().strip()
        # Dimensionen aus der ersten Zeile parsen
        dimensions = myparser.ParseDimension().parse(first_line)
        # Programmabbruch bei ungültiger Dateiformatierung
        if not dimensions:
            print("Invalid input file!")
            return
        # Zur Index-Anpassung vergrößern wir die Dimensionen um 1
        m, n = dimensions[0][0].first+1, dimensions[0][0].second+1

    # Erstellung eines Arrays mit Z3 zur Repräsentation der Matrizen
    A = z3.Array('A', z3.IntSort(), z3.ArraySort(z3.IntSort(), z3.IntSort()))
    # Deklaration und Definition der z3-Variable k
    k = z3.Int('k')
    # Verwendung des Z3-Optimizers
    opt = z3.Optimize()
    # Erhöhung des Timeouts auf 120 Sekunden für längere Berechnungen der Lösung
    opt.set(timeout=120000)

    # Hinzufügen der Bedingungen und Umwandlung in Z3
    for x in range(len(AllConditions)):
        for i in range(m):
            for j in range(n):
                opt.add(eval(AllConditions[x].to_z3()))

    # Minimierung nach Summe aller Elemente der Matrix
    matrix_sum = z3.Sum([A[i][j] for i in range(m) for j in range(n)])
    opt.minimize(matrix_sum)

    # Überprüft, ob eine Lösung vorhanden ist
    if opt.check() == z3.sat:
        model = opt.model()
        # Rückgabe der Lösung als Liste von Listen
        solution = [[model.evaluate(A[i][j]).as_long() for j in range(n)] for i in range(m)]
        # Wir schneiden die Lösung aus der größeren Matrix aus (Beispiel: aus 4x4 Matrix wird 3x3 Matrix)
        solution = solution[1:]
        solution = [row[1:] for row in solution]
        return solution
    else:
        print("No solution found!")
        # Rückgabe der leeren Liste, da keine Lösung gefunden werden konnte
        return []

