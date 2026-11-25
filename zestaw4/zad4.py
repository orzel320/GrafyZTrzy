import heapq
import math

import matplotlib.pyplot as plt
from zad1 import wizualizuj_digraf

from zad3 import bellman_ford, waliduj_digraf_wazony


def dijkstra(n, wagi_nieujemne, start):
    waliduj_digraf_wazony(n, wagi_nieujemne, dozwolone_petle=True)
    if not isinstance(start, int) or isinstance(start, bool) or not 0 <= start < n:
        raise ValueError(f"Wierzchołek startowy {start} poza zakresem [0, {n - 1}].")

    sasiedzi = [[] for _ in range(n)]
    for (u, v), w in wagi_nieujemne.items():
        if w < 0:
            raise ValueError(f"Algorytm Dijkstry wymaga wag nieujemnych (otrzymano {w} na łuku {(u, v)}).")
        sasiedzi[u].append((v, w))

    odleglosci = [math.inf] * n
    poprzednicy = [None] * n
    odleglosci[start] = 0
    kolejka = [(0, start)]

    while kolejka:
        d, u = heapq.heappop(kolejka)
        if d > odleglosci[u]:
            continue
        for v, w in sasiedzi[u]:
            nowa = d + w
            if nowa < odleglosci[v]:
                odleglosci[v] = nowa
                poprzednicy[v] = u
                heapq.heappush(kolejka, (nowa, v))

    return odleglosci, poprzednicy


def johnson(n, wagi, zwroc_szczegoly=False):
    waliduj_digraf_wazony(n, wagi, dozwolone_petle=True)
    if n == 0:
        return ([], [], {}) if zwroc_szczegoly else []

    q = n
    wagi_rozszerzone = {**wagi, **{(q, v): 0 for v in range(n)}}

    h_pelne, _ = bellman_ford(n + 1, wagi_rozszerzone, start=q)
    h = h_pelne[:n]

    wagi_przewazone = {
        (u, v): w + h[u] - h[v]
        for (u, v), w in wagi.items()
    }

    D = []
    for u in range(n):
        d_prim, _ = dijkstra(n, wagi_przewazone, start=u)
        wiersz = [
            math.inf if d == math.inf else d - h[u] + h[v]
            for v, d in enumerate(d_prim)
        ]
        D.append(wiersz)

    return (D, h, wagi_przewazone) if zwroc_szczegoly else D


def weryfikuj_johnsona(n, wagi, D):
    for u in range(n):
        oczekiwany, _ = bellman_ford(n, wagi, start=u)
        if not all(math.isclose(a, b, abs_tol=1e-9) for a, b in zip(D[u], oczekiwany)):
            return False
    return True


def wypisz_macierz_odleglosci(D, od_jedynki=True):
    if not D:
        print("(pusta)")
        return
    baza = 1 if od_jedynki else 0
    tekst = [["∞" if x == math.inf else str(x) for x in wiersz] for wiersz in D]
    szer = max(max(len(x) for w in tekst for x in w), len(str(len(D) - 1 + baza)))
    naglowek = " " * (szer + 2) + " ".join(f"{j + baza:>{szer}}" for j in range(len(D)))
    print(naglowek)
    for i, wiersz in enumerate(tekst):
        print(f"{i + baza:>{szer}}: " + " ".join(f"{x:>{szer}}" for x in wiersz))


def wizualizuj_przewazenie(n, wagi, wagi_przewazone, h, od_jedynki=True):
    _fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 6.5))
    luki = list(wagi.keys())
    wizualizuj_digraf(n, luki, wagi=wagi, tytul="Przed przeważeniem (wagi w)", od_jedynki=od_jedynki, ax=ax1)
    wizualizuj_digraf(
        n, luki, wagi=wagi_przewazone,
        tytul=f"Po przeważeniu (w' ≥ 0), h = {h}",
        od_jedynki=od_jedynki, ax=ax2,
    )
    plt.tight_layout()
    plt.show()