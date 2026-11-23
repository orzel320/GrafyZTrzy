import math
import random
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch


def _sprawdz_int(x, nazwa):
    if not isinstance(x, int) or isinstance(x, bool):
        raise ValueError(f"{nazwa} musi być liczbą całkowitą.")


def waliduj_digraf(n, luki, dozwolone_petle=False):
    _sprawdz_int(n, "n")
    if n < 0:
        raise ValueError("Liczba wierzchołków nie może być ujemna.")

    widziane = set()
    wynik = []
    for u, v in luki:
        _sprawdz_int(u, "u")
        _sprawdz_int(v, "v")
        if not (0 <= u < n and 0 <= v < n):
            raise ValueError(f"Łuk ({u}, {v}) poza zakresem [0, {n - 1}].")
        if not dozwolone_petle and u == v:
            raise ValueError(f"Pętla własna ({u}, {u}) jest niedozwolona.")
        if (u, v) in widziane:
            raise ValueError(f"Powtórzony łuk: ({u}, {v}).")
        widziane.add((u, v))
        wynik.append((u, v))
    return wynik


def konwertuj_digraf(n, luki, dozwolone_petle=False):
    luki = sorted(waliduj_digraf(n, luki, dozwolone_petle))
    if any(u == v for u, v in luki):
        raise ValueError("Macierz incydencji {-1, 0, 1} nie obsługuje pętli własnych.")

    A = [[0] * n for _ in range(n)]
    L = [[] for _ in range(n)]
    B = [[0] * len(luki) for _ in range(n)]

    for j, (u, v) in enumerate(luki):
        A[u][v] = 1
        L[u].append(v)
        B[u][j], B[v][j] = -1, 1

    return A, B, L


def generuj_digraf_gnp(n, p, seed=None):
    """Generuje losowy digraf prosty w modelu G(n, p)."""
    _sprawdz_int(n, "n")
    if n < 0:
        raise ValueError("Liczba wierzchołków nie może być ujemna.")
    if not isinstance(p, (int, float)) or isinstance(p, bool) or not math.isfinite(p):
        raise ValueError("p musi być skończoną liczbą rzeczywistą.")
    if not 0.0 <= p <= 1.0:
        raise ValueError("p musi należeć do [0, 1].")

    rng = random.Random(seed)
    return [(i, j) for i in range(n) for j in range(n) if i != j and rng.random() < p]


def wczytaj_digraf(nazwa, dozwolone_petle=False):
    with open(nazwa, "r", encoding="utf-8") as f:
        linie = [l.split("#", 1)[0].strip() for l in f]
        linie = [l for l in linie if l]

    if not linie:
        raise ValueError("Plik jest pusty.")
    if linie == ["0"]:
        return 0, []

    pierwsza = linie[0].split()

    if pierwsza[0][-1] in (".", ":") and pierwsza[0][:-1].isdigit():
        etykiety, wiersze = [], []
        for linia in linie:
            tok = linia.split()
            if tok[0][-1] not in (".", ":") or not tok[0][:-1].isdigit():
                raise ValueError(f"Niepoprawna etykieta wiersza: '{linia}'.")
            etykiety.append(int(tok[0][:-1]))
            wiersze.append([int(x) for x in tok[1:]])
        n, baza = len(etykiety), etykiety[0]
        if baza not in (0, 1) or etykiety != list(range(baza, baza + n)):
            raise ValueError("Etykiety wierzchołków muszą tworzyć ciąg 0..n-1 lub 1..n.")
        luki = [(u, v - baza) for u, sas in enumerate(wiersze) for v in sas]
        return n, waliduj_digraf(n, luki, dozwolone_petle)

    ma_nm = (
        len(pierwsza) == 2
        and all(t.isdigit() for t in pierwsza)
        and (
            (int(pierwsza[1]) == 0 and len(linie) == 1)
            or (len(linie) == int(pierwsza[0]) + 1 and len(linie[1].split()) == int(pierwsza[1]))
        )
    )
    if ma_nm or any("-1" in linia.split() for linia in linie):
        if ma_nm:
            n, m = int(pierwsza[0]), int(pierwsza[1])
            if m == 0:
                return n, []
            B = [[int(x) for x in w.split()] for w in linie[1:]]
        else:
            B = [[int(x) for x in w.split()] for w in linie]
            n, m = len(B), len(B[0])

        if len(B) != n or any(len(r) != m for r in B):
            raise ValueError("Niepoprawne wymiary macierzy incydencji.")
        if any(x not in (-1, 0, 1) for r in B for x in r):
            raise ValueError("Macierz incydencji może zawierać tylko -1, 0 i 1.")

        luki = []
        for j in range(m):
            od = [i for i in range(n) if B[i][j] == -1]
            do = [i for i in range(n) if B[i][j] == 1]
            if len(od) != 1 or len(do) != 1:
                raise ValueError(f"Kolumna {j} musi mieć dokładnie jedno -1 i jedno 1.")
            luki.append((od[0], do[0]))
        return n, waliduj_digraf(n, luki, dozwolone_petle=False)

    if len(pierwsza) == 1 and pierwsza[0].isdigit() and len(linie) == int(pierwsza[0]) + 1:
        linie = linie[1:]
    A = [[int(x) for x in w.split()] for w in linie]
    n = len(A)
    if any(len(r) != n for r in A) or any(x not in (0, 1) for r in A for x in r):
        raise ValueError("Niepoprawna macierz sąsiedztwa (oczekiwano macierzy n x n z {0, 1}).")

    luki = [(i, j) for i in range(n) for j in range(n) if A[i][j] == 1]
    return n, waliduj_digraf(n, luki, dozwolone_petle)


def wypisz_macierz(M):
    if not M or not M[0]:
        print("(pusta)")
        return
    szer = max(len(str(x)) for r in M for x in r)
    for r in M:
        print(" ".join(f"{x:>{szer}}" for x in r))


def wypisz_liste_sasiedztwa(L, od_jedynki=True):
    baza = 1 if od_jedynki else 0
    for u, sas in enumerate(L):
        print(f"{u + baza}. {' '.join(str(v + baza) for v in sas)}".rstrip())


def _punkt_na_luku(x1, y1, x2, y2, rad, t):
    cx = 0.5 * (x1 + x2) + rad * (y2 - y1)
    cy = 0.5 * (y1 + y2) - rad * (x2 - x1)
    u = 1.0 - t
    return (
        u * u * x1 + 2 * u * t * cx + t * t * x2,
        u * u * y1 + 2 * u * t * cy + t * t * y2,
    )


def _wybierz_pozycje_etykiety(x1, y1, x2, y2, rad, zajete, min_odl=0.95):
    kandydaci = [
        _punkt_na_luku(x1, y1, x2, y2, rad, t)
        for t in (0.34, 0.66, 0.26, 0.74, 0.5, 0.42, 0.58)
    ]
    najlepszy, max_odl = kandydaci[0], -1.0
    for px, py in kandydaci:
        odl = min(math.hypot(px - zx, py - zy) for zx, zy in zajete)
        if odl >= min_odl:
            return px, py
        if odl > max_odl:
            najlepszy, max_odl = (px, py), odl
    return najlepszy


def wizualizuj_digraf(n, luki, wagi=None, kolory=None, tytul="Digraf", od_jedynki=True, ax=None):
    if n == 0:
        print("Digraf pusty (0 wierzchołków).")
        return

    pokaz = ax is None
    if ax is None:
        _, ax = plt.subplots(figsize=(7, 7))

    r = 0.0 if n == 1 else 5.0
    pos = [(r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n)) for i in range(n)]
    zbior, baza = set(luki), (1 if od_jedynki else 0)
    zajete = list(pos)

    for u, v in luki:
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        if u == v:
            nx, ny = math.cos(2 * math.pi * u / n), math.sin(2 * math.pi * u / n)
            ax.add_patch(plt.Circle((x1 + 0.85 * nx, y1 + 0.85 * ny), 0.55, fill=False, ec="#444", lw=1.4))
            xm, ym = x1 + 1.55 * nx, y1 + 1.55 * ny
        else:
            rad = 0.18 if (v, u) in zbior else 0.06
            ax.add_patch(FancyArrowPatch(
                (x1, y1), (x2, y2), connectionstyle=f"arc3,rad={rad}",
                arrowstyle="-|>,head_length=8,head_width=4.5", shrinkA=18, shrinkB=18,
                color="#333", lw=1.4, zorder=1,
            ))
            xm, ym = _wybierz_pozycje_etykiety(x1, y1, x2, y2, rad, zajete)

        if wagi is not None and (u, v) in wagi:
            zajete.append((xm, ym))
            w = wagi[(u, v)]
            ax.text(
                xm, ym, str(w), ha="center", va="center", fontsize=9.5, fontweight="bold",
                color="#b30000" if w < 0 else "#1a1a1a",
                bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="#ffffff", lw=0.6, alpha=1.0),
                zorder=4,
            )

    kolory = kolory or ["#c6d9ff"] * n
    for i, (xi, yi) in enumerate(pos):
        ax.scatter(xi, yi, s=650, color=kolory[i], edgecolors="#1d2d7a", lw=1.5, zorder=2)
        ax.text(xi, yi, str(i + baza), ha="center", va="center", fontsize=11, fontweight="bold", zorder=3)

    ax.set_title(tytul)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(-r - 2, r + 2)
    ax.set_ylim(-r - 2, r + 2)
    if pokaz:
        plt.tight_layout()
        plt.show()