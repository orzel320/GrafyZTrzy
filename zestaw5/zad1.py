import math
import random
from collections import deque

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch


def _sprawdz_int(x, nazwa):
    if not isinstance(x, int) or isinstance(x, bool):
        raise TypeError(f"{nazwa} musi być liczbą całkowitą.")


def etykiety_wierzcholkow(n):
    if n < 2:
        return [str(i) for i in range(n)]
    posrednie = (
        [chr(ord("a") + i) for i in range(n - 2)]
        if n - 2 <= 26
        else [f"v{i + 1}" for i in range(n - 2)]
    )
    return ["s", *posrednie, "t"]


def waliduj_siec(n, pojemnosci, s=0, t=None, zezwalaj_przeciwbiezne=False):
    _sprawdz_int(n, "n")
    if n < 2:
        raise ValueError("Sieć przepływowa musi mieć co najmniej 2 wierzchołki (źródło i ujście).")
    if t is None:
        t = n - 1
    _sprawdz_int(s, "s")
    _sprawdz_int(t, "t")
    if not (0 <= s < n and 0 <= t < n) or s == t:
        raise ValueError("Źródło s i ujście t muszą być różnymi wierzchołkami z [0, n-1].")

    for (u, v), c in pojemnosci.items():
        _sprawdz_int(u, "u")
        _sprawdz_int(v, "v")
        if not (0 <= u < n and 0 <= v < n):
            raise ValueError(f"Łuk {(u, v)} poza zakresem [0, {n - 1}].")
        if u == v:
            raise ValueError(f"Pętla własna {(u, u)} jest niedozwolona w sieci przepływowej.")
        if v == s:
            raise ValueError(f"Łuk {(u, v)} nie może wchodzić do źródła s.")
        if u == t:
            raise ValueError(f"Łuk {(u, v)} nie może wychodzić z ujścia t.")
        if not isinstance(c, (int, float)) or isinstance(c, bool) or not math.isfinite(c) or c < 0:
            raise ValueError(f"Przepustowość łuku {(u, v)} musi być nieujemną liczbą skończoną.")
        if not zezwalaj_przeciwbiezne and (v, u) in pojemnosci:
            raise ValueError(f"Niedozwolone łuki przeciwbieżne: {(u, v)} i {(v, u)}.")

    return pojemnosci


def generuj_siec(N, min_c=1, max_c=10, seed=None):
    _sprawdz_int(N, "N")
    if N < 2:
        raise ValueError("Liczba warstw pośrednich N musi spełniać N >= 2.")
    _sprawdz_int(min_c, "min_c")
    _sprawdz_int(max_c, "max_c")
    if min_c < 0 or min_c > max_c:
        raise ValueError("Wymagane 0 <= min_c <= max_c.")

    rng = random.Random(seed)

    warstwy = [[0]]
    nastepny = 1
    for _ in range(N):
        rozmiar = rng.randint(2, N)
        warstwy.append(list(range(nastepny, nastepny + rozmiar)))
        nastepny += rozmiar
    warstwy.append([nastepny])
    n = nastepny + 1
    s, t = 0, n - 1

    luki = set()
    for i in range(N + 1):
        lewa = list(warstwy[i])
        prawa = list(warstwy[i + 1])
        rng.shuffle(lewa)
        rng.shuffle(prawa)
        for k in range(max(len(lewa), len(prawa))):
            u = lewa[k] if k < len(lewa) else rng.choice(lewa)
            v = prawa[k] if k < len(prawa) else rng.choice(prawa)
            luki.add((u, v))

    zajete_pary = {tuple(sorted(luk)) for luk in luki}
    wolne_pary = [
        (u, v) for u in range(n) for v in range(u + 1, n) if (u, v) not in zajete_pary
    ]
    for u, v in rng.sample(wolne_pary, 2 * N):
        if u == s or v == t:
            luki.add((u, v))
        else:
            luki.add((u, v) if rng.random() < 0.5 else (v, u))

    pojemnosci = {luk: rng.randint(min_c, max_c) for luk in sorted(luki)}
    return warstwy, pojemnosci


def _wyznacz_warstwy_bfs(n, pojemnosci, s, t):
    sasiedzi = [[] for _ in range(n)]
    for u, v in pojemnosci:
        sasiedzi[u].append(v)

    odl = {s: 0}
    kolejka = deque([s])
    while kolejka:
        u = kolejka.popleft()
        for v in sasiedzi[u]:
            if v not in odl:
                odl[v] = odl[u] + 1
                kolejka.append(v)

    grupy = {}
    for v in range(n):
        if v in (s, t):
            continue
        grupy.setdefault(odl.get(v, n), []).append(v)

    return [[s], *[grupy[k] for k in sorted(grupy)], [t]]


def wczytaj_siec(nazwa, zezwalaj_przeciwbiezne=False):
    with open(nazwa, "r", encoding="utf-8") as f:
        linie = [l.split("#", 1)[0].strip() for l in f]
        linie = [l for l in linie if l]

    if not linie:
        raise ValueError("Plik jest pusty.")

    pierwsza = linie[0].split()
    if len(pierwsza) != 2:
        raise ValueError("Pierwsza linia musi zawierać etykiety źródła i ujścia: 's t'.")
    nazwa_s, nazwa_t = pierwsza
    if nazwa_s == nazwa_t:
        raise ValueError("Źródło i ujście muszą mieć różne etykiety.")

    indeks_start = 1
    jawne_warstwy = None
    if len(linie) > 1 and linie[1].lower().startswith("warstwy:"):
        czesc = linie[1].split(":", 1)[1]
        jawne_warstwy = [grupa.split() for grupa in czesc.split("|") if grupa.split()]
        indeks_start = 2

    surowe_luki = []
    etykiety_posrednie = []
    widziane = {nazwa_s, nazwa_t}

    if jawne_warstwy:
        for grupa in jawne_warstwy:
            for nazwa_w in grupa:
                if nazwa_w not in widziane:
                    widziane.add(nazwa_w)
                    etykiety_posrednie.append(nazwa_w)

    for linia in linie[indeks_start:]:
        tok = linia.split()
        if len(tok) != 3:
            raise ValueError(f"Niepoprawny wiersz łuku: '{linia}'. Oczekiwano 'u v c'.")
        u_str, v_str, c_str = tok
        for nazwa_w in (u_str, v_str):
            if nazwa_w not in widziane:
                widziane.add(nazwa_w)
                etykiety_posrednie.append(nazwa_w)
        c = int(c_str) if c_str.lstrip("-").isdigit() else float(c_str)
        surowe_luki.append((u_str, v_str, c))

    etykiety = [nazwa_s, *etykiety_posrednie, nazwa_t]
    nr = {nazwa_w: i for i, nazwa_w in enumerate(etykiety)}
    n = len(etykiety)

    pojemnosci = {}
    for u_str, v_str, c in surowe_luki:
        luk = (nr[u_str], nr[v_str])
        if luk in pojemnosci:
            raise ValueError(f"Powtórzony łuk: ({u_str}, {v_str}).")
        pojemnosci[luk] = c

    waliduj_siec(n, pojemnosci, s=0, t=n - 1, zezwalaj_przeciwbiezne=zezwalaj_przeciwbiezne)

    if jawne_warstwy is not None:
        warstwy = [[nr[w] for w in grupa] for grupa in jawne_warstwy]
        splaszczone = [w for grupa in warstwy for w in grupa]
        if len(splaszczone) != n or set(splaszczone) != set(range(n)):
            raise ValueError("Linia 'warstwy:' musi zawierać każdy wierzchołek sieci dokładnie raz.")
        if len(warstwy) < 2 or warstwy[0] != [0] or warstwy[-1] != [n - 1]:
            raise ValueError("Pierwsza warstwa musi zawierać wyłącznie źródło, a ostatnia wyłącznie ujście.")
    else:
        warstwy = _wyznacz_warstwy_bfs(n, pojemnosci, s=0, t=n - 1)

    return warstwy, pojemnosci, etykiety


def _punkt_na_luku(x1, y1, x2, y2, rad, t):
    cx = 0.5 * (x1 + x2) + rad * (y2 - y1)
    cy = 0.5 * (y1 + y2) - rad * (x2 - x1)
    u = 1.0 - t
    return (
        u * u * x1 + 2 * u * t * cx + t * t * x2,
        u * u * y1 + 2 * u * t * cy + t * t * y2,
    )


def _wybierz_pozycje_etykiety(x1, y1, x2, y2, rad, zajete, min_odl=0.75):
    kandydaci = [
        _punkt_na_luku(x1, y1, x2, y2, rad, t)
        for t in (0.36, 0.64, 0.5, 0.28, 0.72, 0.43, 0.57)
    ]
    najlepszy, max_odl = kandydaci[0], -1.0
    for px, py in kandydaci:
        odl = min(math.hypot(px - zx, py - zy) for zx, zy in zajete)
        if odl >= min_odl:
            return px, py
        if odl > max_odl:
            najlepszy, max_odl = (px, py), odl
    return najlepszy


def wizualizuj_siec(
    warstwy,
    pojemnosci,
    przeplyw=None,
    sciezka=None,
    etykiety=None,
    tytul="Sieć przepływowa",
    rezydualna=False,
    ax=None,
):
    n = sum(len(w) for w in warstwy)
    etykiety = etykiety or etykiety_wierzcholkow(n)
    s, t = warstwy[0][0], warstwy[-1][0]

    pokaz = ax is None
    if ax is None:
        _, ax = plt.subplots(figsize=(max(8.5, 2.3 * len(warstwy)), 5.8))

    pos, nr_warstwy, poz_w_warstwie = {}, {}, {}
    for nr_w, grupa in enumerate(warstwy):
        x_baz = nr_w * 3.4
        dy_warstwy = 0.0 if nr_w in (0, len(warstwy) - 1) else (0.28 if nr_w % 2 else -0.28)
        m = len(grupa)
        for k, v in enumerate(grupa):
            y = ((m - 1) / 2.0 - k) * 2.4 + dy_warstwy
            dx = (0.32 if k % 2 else -0.32) if m >= 3 else 0.0
            pos[v] = (x_baz + dx, y)
            nr_warstwy[v], poz_w_warstwie[v] = nr_w, k

    zbior_sciezki = set(sciezka or [])
    zajete = list(pos.values())

    for (u, v), c in pojemnosci.items():
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        na_sciezce = (u, v) in zbior_sciezki
        skok = abs(nr_warstwy[u] - nr_warstwy[v])
        skok_kol = abs(poz_w_warstwie[u] - poz_w_warstwie[v]) if skok == 0 else 0

        if (v, u) in pojemnosci:
            rad = 0.26 if (skok >= 2 or skok_kol >= 2) else 0.16
        elif skok >= 2:
            kierunek = (-1 if (y1 + y2) >= 0 else 1) * (1 if x2 >= x1 else -1)
            rad = kierunek * min(0.35, 0.18 + 0.06 * (skok - 1))
        elif skok_kol >= 2:
            rad = 0.24
        else:
            rad = 0.04
        kolor_luku = "#c62828" if na_sciezce else ("#1b5e20" if rezydualna else "#222222")

        ax.add_patch(FancyArrowPatch(
            (x1, y1), (x2, y2), connectionstyle=f"arc3,rad={rad}",
            arrowstyle="-|>,head_length=8,head_width=4.5", shrinkA=20, shrinkB=20,
            color=kolor_luku, lw=2.3 if na_sciezce else 1.4, zorder=1,
        ))

        xm, ym = _wybierz_pozycje_etykiety(x1, y1, x2, y2, rad, zajete)
        zajete.append((xm, ym))
        tekst = str(c) if przeplyw is None else f"{przeplyw[(u, v)]}/{c}"
        ax.text(
            xm, ym, tekst, ha="center", va="center", fontsize=9.5, fontweight="bold",
            color=kolor_luku,
            bbox={"boxstyle": "round,pad=0.18", "fc": "white", "ec": "#ffffff", "lw": 0.6, "alpha": 1.0},
            zorder=4,
        )

    kolor_wyp = "#d9f2e1" if rezydualna else "#d4ddff"
    kolor_ramki = "#1b5e20" if rezydualna else "#1d2d7a"

    for v, (xv, yv) in pos.items():
        if v in (s, t):
            ax.scatter(xv, yv, s=1050, color="white", edgecolors=kolor_ramki, lw=1.6, zorder=2)
        ax.scatter(xv, yv, s=680, color=kolor_wyp, edgecolors=kolor_ramki, lw=1.5, zorder=2.5)
        ax.text(xv, yv, etykiety[v], ha="center", va="center", fontsize=11, fontweight="bold", zorder=3)

    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    ax.set_title(tytul)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(min(xs) - 1.6, max(xs) + 1.6)
    ax.set_ylim(min(ys) - 1.6, max(ys) + 1.6)
    if pokaz:
        plt.tight_layout()
        plt.show()