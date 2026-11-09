import math
import random
import matplotlib.pyplot as plt

def generuj_gnl(n, l):
    if n < 0:
        raise ValueError("Liczba wierzchołków nie może być ujemna.")

    maks_krawedzi = n * (n - 1) // 2

    if not isinstance(l, int) or isinstance(l, bool):
        raise ValueError("Liczba krawędzi musi być liczbą całkowitą.")

    if l < 0 or l > maks_krawedzi:
        raise ValueError(
            f"Dla n = {n} można utworzyć od 0 do "
            f"{maks_krawedzi} krawędzi."
        )

    mozliwe_krawedzie = [
        (i, j)
        for i in range(n)
        for j in range(i + 1, n)
    ]

    krawedzie = random.sample(mozliwe_krawedzie, l)

    return krawedzie

def generuj_gnp(n, p):
    if n < 0:
        raise ValueError("Liczba wierzchołków nie może być ujemna.")

    if not isinstance(p, (int, float)) or isinstance(p, bool):
        raise ValueError("Prawdopodobieństwo musi być liczbą.")

    if not 0 <= p <= 1:
        raise ValueError("Prawdopodobieństwo p musi należeć do [0, 1].")

    krawedzie = []

    for i in range(n):
        for j in range(i + 1, n):
            if random.random() < p:
                krawedzie.append((i, j))

    return krawedzie

def wizualizuj_graf(n, krawedzie, tytul="Graf losowy"):
    if n == 0:
        print("Graf nie ma wierzchołków.")
        return

    # parametry okręgu
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
            xi, yi,
            s=600,
            color="skyblue",
            edgecolors="black",
            zorder=2
        )

        ax.text(
            xi, yi, str(i),
            ha="center",
            va="center",
            fontsize=11,
            zorder=3
        )

    ax.set_title(tytul)
    ax.set_aspect("equal")
    ax.axis("off")

    margines = 1.5
    ax.set_xlim(x0 - r - margines, x0 + r + margines)
    ax.set_ylim(y0 - r - margines, y0 + r + margines)

    plt.tight_layout()
    plt.show()

def main():
    print("GENERATOR GRAFÓW LOSOWYCH")
    print("1 - Model G(n, l)")
    print("2 - Model G(n, p)")

    wybor = input("Wybierz model: ").strip()

    try:
        n = int(input("Podaj liczbę wierzchołków n: "))

        if n < 0:
            raise ValueError(
                "Liczba wierzchołków nie może być ujemna."
            )

        if wybor == "1":
            l = int(input("Podaj liczbę krawędzi l: "))
            krawedzie = generuj_gnl(n, l)
            tytul = f"Graf losowy G({n}, {l})"

        elif wybor == "2":
            p = float(input("Podaj prawdopodobieństwo p (0-1): "))
            krawedzie = generuj_gnp(n, p)
            tytul = f"Graf losowy G({n}, {p})"

        else:
            raise ValueError("Niepoprawny wybór modelu.")

        print("\nWylosowane krawędzie:")
        print(krawedzie)
        print("Liczba krawędzi:", len(krawedzie))

        wizualizuj_graf(n, krawedzie, tytul)

    except ValueError as blad:
        print("Błąd:", blad)


if __name__ == "__main__":
    main()
