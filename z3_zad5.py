"""Zadanie 5: algorytm Prima, bez kopca, klas i dodatkowych struktur."""

from z3_zad1 import sprawdz_graf, wizualizuj_graf  # Wspólna kontrola i rysowanie z zadania 1.


def prim(w):
    sprawdz_graf(w)  # Kontrola wejściowej macierzy.
    n = len(w)  # Liczba wierzchołków.
    w_drzewie = [False] * n  # Czy wierzchołek jest już w drzewie T?
    koszt = [float("inf")] * n  # Najtańsza znana krawędź z T do danego wierzchołka.
    rodzic = [None] * n  # Drugi koniec tej najtańszej krawędzi, leżący w T.
    koszt[0] = 0  # Rozpoczynamy od wierzchołka 0; nie potrzebuje on krawędzi.
    drzewo = []  # Wynik: lista trójek (u, v, waga), indeksy od 0.
    suma = 0  # Łączna waga zaakceptowanych krawędzi.
    for krok in range(n):  # W każdej iteracji dodamy jeden wierzchołek.
        u = -1  # Jeszcze nie wybrano wierzchołka.
        minimum = float("inf")  # Szukamy najlżejszej krawędzi do T.
        for v in range(n):  # Liniowy przegląd kandydatów.
            if not w_drzewie[v] and koszt[v] < minimum:
                minimum = koszt[v]  # Nowe minimum.
                u = v  # Wierzchołek, który dołączymy.
        if u == -1:  # Nie istnieje krawędź łącząca T z pozostałą częścią grafu.
            raise ValueError("Graf niespójny: drzewo rozpinające nie istnieje.")
        w_drzewie[u] = True  # Dołączamy wybrany wierzchołek do T.
        if rodzic[u] is not None:  # Pierwszy wierzchołek nie ma rodzica.
            drzewo.append((rodzic[u], u, koszt[u]))  # Dodajemy łączącą krawędź.
            suma += koszt[u]  # Powiększamy wagę drzewa.
        for v in range(n):  # Nowy wierzchołek może oferować tańsze połączenia.
            if w[u][v] > 0 and not w_drzewie[v]:  # Tylko rzeczywiste krawędzie do W.
                if w[u][v] < koszt[v]:  # Uwaga: porównujemy wagę krawędzi, nie długość drogi.
                    koszt[v] = w[u][v]  # Najtańszy aktualny sposób dołączenia v.
                    rodzic[v] = u  # Zapamiętujemy drugi koniec tej krawędzi.
    return drzewo, suma  # Dla n=1 otrzymamy pustą listę i sumę 0.


def wypisz_drzewo(w):
    drzewo, suma = prim(w)  # Obliczamy minimalne drzewo.
    for u, v, waga in drzewo:  # Wypisujemy każdą krawędź.
        print(u + 1, "--", v + 1, "waga:", waga)  # Numery na ekranie od 1.
    print("Suma wag drzewa:", suma)
    wizualizuj_graf(w, "Zadanie 5: minimalne drzewo, suma wag = " + str(suma), drzewo)
