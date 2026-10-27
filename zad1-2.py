import math
import matplotlib.pyplot as plt

def wczytaj_plik(nazwa):
    with open(nazwa, "r", encoding="utf-8") as plik:
        linie = [linia.strip() for linia in plik]

    if not linie:
        raise ValueError("Plik jest pusty.")

    while linie and not linie[0]:
        linie.pop(0)
    while linie and not linie[-1]:
        linie.pop()

    if not linie:
        raise ValueError("Plik jest pusty.")

    pierwsza = linie[0].split()

    # macierz incydencji: 2 liczby
    if len(pierwsza) == 2:
        n, m = map(int, pierwsza)

        if n < 0 or m < 0 or len(linie) != n + 1:
            raise ValueError("Niepoprawne wymiary macierzy.")

        B = [list(map(int, linia.split()))
             for linia in linie[1:]]

        if any(len(row) != m for row in B):
            raise ValueError("Niepoprawna liczba kolumn.")

        if any(x not in (0, 1) for row in B for x in row):
            raise ValueError("Macierz musi zawierać 0 i 1.")

        krawedzie = []

        for j in range(m):
            konce = [i for i in range(n) if B[i][j] == 1]

            if len(konce) != 2:
                raise ValueError(
                    "Każda kolumna macierzy incydencji "
                    "musi zawierać dokładnie dwie jedynki."
                )

            krawedzie.append(tuple(konce))

        if len(set(tuple(sorted(e)) for e in krawedzie)) != m:
            raise ValueError("Powtórzone krawędzie.")

        return n, krawedzie

    # pozostale to liczba wierzchowlkow
    if len(pierwsza) != 1:
        raise ValueError("Nie można rozpoznać formatu pliku.")

    n = int(pierwsza[0])

    if n < 0 or len(linie) != n + 1:
        raise ValueError("Niepoprawna liczba wierszy.")

    dane = []
    for linia in linie[1:]:
        dane.append(
            list(map(int, linia.split())) if linia else []
        )

    # Kandydat 1: macierz sasiedztwa
    macierz = (
        all(len(row) == n for row in dane)
        and all(x in (0, 1) for row in dane for x in row)
        and all(dane[i][i] == 0 for i in range(n))
        and all(
            dane[i][j] == dane[j][i]
            for i in range(n) for j in range(n)
        )
    )

    # Kandydat 2: lista sasiedztwa
    lista = True
    for i, sasiedzi in enumerate(dane):
        if len(sasiedzi) != len(set(sasiedzi)):
            lista = False
            break

        for j in sasiedzi:
            if not 0 <= j < n or j == i:
                lista = False
                break
            if i not in dane[j]:
                lista = False
                break

    if macierz and lista:
        raise ValueError(
            "Format jest niejednoznaczny: dane mogą być "
            "macierzą sąsiedztwa lub listą sąsiedztwa. "
            "Dodaj oznaczenie typu albo zmień format pliku."
        )

    if macierz:
        krawedzie = [
            (i, j)
            for i in range(n)
            for j in range(i + 1, n)
            if dane[i][j] == 1
        ]
        return n, krawedzie

    if lista:
        krawedzie = [
            (i, j)
            for i in range(n)
            for j in dane[i]
            if i < j
        ]
        return n, krawedzie

    raise ValueError(
        "Nie rozpoznano reprezentacji grafu. "
        "Sprawdź dane w pliku."
    )



def konwertuj(n, krawedzie):
    # macierz sasiedztwa
    A = [[0] * n for _ in range(n)]

    # lista sasiedztwa
    L = [[] for _ in range(n)]

    for u, v in krawedzie:
        A[u][v] = 1
        A[v][u] = 1

        L[u].append(v)
        L[v].append(u)

    for sasiedzi in L:
        sasiedzi.sort()

    # macierz incydencji
    m = len(krawedzie)
    B = [[0] * m for _ in range(n)]

    for j, (u, v) in enumerate(krawedzie):
        B[u][j] = 1
        B[v][j] = 1

    return A, B, L


def wypisz_macierz(macierz):
    if not macierz:
        print("(pusta)")
    else:
        for wiersz in macierz:
            print(*wiersz)

def wizualizuj_graf(n, krawedzie):

    if n == 0:
        print("Graf nie ma wierzchołków.")
        return

    # parametry okregu
    x0 = 0
    y0 = 0
    r = 5

    alfa = 2 * math.pi / n

    polozenia = []

    for i in range(n):
        xi = x0 + r * math.cos(i * alfa)
        yi = y0 + r * math.sin(i * alfa)

        polozenia.append((xi, yi))

    fig, ax = plt.subplots(figsize=(8, 8))

    for u, v in krawedzie:
        x1, y1 = polozenia[u]
        x2, y2 = polozenia[v]

        ax.plot(
            [x1, x2],
            [y1, y2],
            color="gray",
            linewidth=1.5,
            zorder=1
        )

    for i, (xi, yi) in enumerate(polozenia):
        ax.scatter(
            xi,
            yi,
            s=600,
            color="skyblue",
            edgecolors="black",
            zorder=2
        )

        ax.text(
            xi,
            yi,
            str(i),
            ha="center",
            va="center",
            fontsize=11,
            zorder=3
        )

    ax.set_title("Wizualizacja grafu prostego")
    ax.set_aspect("equal")
    ax.axis("off")

    margines = 1.5
    ax.set_xlim(x0 - r - margines, x0 + r + margines)
    ax.set_ylim(y0 - r - margines, y0 + r + margines)

    plt.show()


def main():
    nazwa = input("Podaj nazwę pliku: ")

    try:
        n, krawedzie = wczytaj_plik(nazwa)
        A, B, L = konwertuj(n, krawedzie)

        print("\nMACIERZ SĄSIEDZTWA:")
        wypisz_macierz(A)

        print("\nMACIERZ INCYDENCJI:")
        wypisz_macierz(B)

        print("\nLISTA SĄSIEDZTWA:")
        for i, sasiedzi in enumerate(L):
            print(f"{i}: {sasiedzi}")

        wizualizuj_graf(n, krawedzie)

    except (ValueError, IndexError, OSError) as blad:
        print("Błąd:", blad)


if __name__ == "__main__":
    main()
