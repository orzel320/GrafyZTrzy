from collections import deque

import matplotlib.pyplot as plt
from zad1 import waliduj_siec, wizualizuj_siec


def siec_rezydualna(pojemnosci, przeplyw):
    c_f = {}
    for (u, v), c in pojemnosci.items():
        f = przeplyw[(u, v)]
        if c - f > 0:
            c_f[(u, v)] = c_f.get((u, v), 0) + (c - f)
        if f > 0:
            c_f[(v, u)] = c_f.get((v, u), 0) + f
    return c_f


def bfs_sciezka(n, c_f, s, t):
    sasiedzi = [[] for _ in range(n)]
    for (u, v), cap in c_f.items():
        if cap > 0:
            sasiedzi[u].append(v)
    for lista in sasiedzi:
        lista.sort()

    poprzednik = {s: None}
    kolejka = deque([s])

    while kolejka:
        u = kolejka.popleft()
        if u == t:
            sciezka = []
            while poprzednik[u] is not None:
                sciezka.append((poprzednik[u], u))
                u = poprzednik[u]
            return list(reversed(sciezka))
        for v in sasiedzi[u]:
            if v not in poprzednik:
                poprzednik[v] = u
                kolejka.append(v)

    return None


def _rozbij_przeciwbiezne(n, pojemnosci):
    nowe = {}
    rozbite = {}
    nastepny = n

    for (u, v), c in pojemnosci.items():
        if (v, u) in pojemnosci and u > v:
            w = nastepny
            nastepny += 1
            nowe[(u, w)] = c
            nowe[(w, v)] = c
            rozbite[(u, v)] = w
        else:
            nowe[(u, v)] = c

    return nastepny, nowe, rozbite


def _edmonds_karp(n, pojemnosci, s, t, historia=False):
    przeplyw = {luk: 0 for luk in pojemnosci}
    kroki = []

    while True:
        c_f = siec_rezydualna(pojemnosci, przeplyw)
        sciezka = bfs_sciezka(n, c_f, s, t)
        if sciezka is None:
            break

        cf_p = min(c_f[luk] for luk in sciezka)
        cofanie = any(luk not in pojemnosci for luk in sciezka)

        for u, v in sciezka:
            if (u, v) in pojemnosci:
                przeplyw[(u, v)] += cf_p
            else:
                przeplyw[(v, u)] -= cf_p

        if historia:
            kroki.append((sciezka, cf_p, cofanie, dict(przeplyw), c_f))

    return przeplyw, kroki


def ford_fulkerson(n, pojemnosci, s=0, t=None, rozbij_przeciwbiezne=False, historia=False):
    if t is None:
        t = n - 1
    waliduj_siec(n, pojemnosci, s, t, zezwalaj_przeciwbiezne=rozbij_przeciwbiezne)

    def _zwin_sciezke(sciezka, n):
        wynik, i = [], 0
        while i < len(sciezka):
            u, v = sciezka[i]
            if v >= n:
                wynik.append((u, sciezka[i + 1][1]))
                i += 2
            else:
                wynik.append((u, v))
                i += 1
        return wynik


    def _rzutuj_przeplyw(przeplyw_rob, pojemnosci, rozbite):
        return {
            luk: przeplyw_rob[(luk[0], rozbite[luk])] if luk in rozbite else przeplyw_rob[luk]
            for luk in pojemnosci
        }

    if rozbij_przeciwbiezne:
        n_rob, poj_rob, rozbite = _rozbij_przeciwbiezne(n, pojemnosci)
        przeplyw_rob, kroki_rob = _edmonds_karp(n_rob, poj_rob, s, t, historia=historia)
        przeplyw = _rzutuj_przeplyw(przeplyw_rob, pojemnosci, rozbite)
        kroki = []
        poprzedni = {luk: 0 for luk in pojemnosci}
        for sciezka_rob, cf_p, cofanie, p_rob, _ in kroki_rob:
            p_oryg = _rzutuj_przeplyw(p_rob, pojemnosci, rozbite)
            kroki.append((
                _zwin_sciezke(sciezka_rob, n), cf_p, cofanie, p_oryg,
                siec_rezydualna(pojemnosci, poprzedni),
            ))
            poprzedni = p_oryg
    else:
        przeplyw, kroki = _edmonds_karp(n, pojemnosci, s, t, historia=historia)

    wartosc = sum(f for (u, _), f in przeplyw.items() if u == s)
    return (wartosc, przeplyw, kroki) if historia else (wartosc, przeplyw)


def weryfikuj_przeplyw(n, pojemnosci, przeplyw, s=0, t=None, zezwalaj_przeciwbiezne=False):
    if t is None:
        t = n - 1
    waliduj_siec(n, pojemnosci, s, t, zezwalaj_przeciwbiezne=zezwalaj_przeciwbiezne)

    for luk, c in pojemnosci.items():
        if not 0 <= przeplyw[luk] <= c:
            return False

    bilans = [0] * n
    for (u, v), f in przeplyw.items():
        bilans[u] -= f
        bilans[v] += f
    if any(bilans[u] != 0 for u in range(n) if u not in (s, t)):
        return False

    wartosc_s = -bilans[s]
    if wartosc_s != bilans[t]:
        return False

    c_f = siec_rezydualna(pojemnosci, przeplyw)
    osiagalne = {s}
    kolejka = deque([s])
    while kolejka:
        u = kolejka.popleft()
        for (a, b), cap in c_f.items():
            if a == u and cap > 0 and b not in osiagalne:
                osiagalne.add(b)
                kolejka.append(b)

    if t in osiagalne:
        return False

    przekroj = sum(c for (u, v), c in pojemnosci.items() if u in osiagalne and v not in osiagalne)
    return przekroj == wartosc_s


def wypisz_historie(kroki, etykiety=None):
    for i, (sciezka, cf_p, cofanie, _, _) in enumerate(kroki, start=1):
        wierzcholki = [sciezka[0][0], *[v for _, v in sciezka]]
        trasa = " -> ".join(etykiety[w] if etykiety else str(w) for w in wierzcholki)
        uwaga = "  [cofanie przepływu]" if cofanie else ""
        print(f"Iteracja {i}: {trasa} | c_f(p) = {cf_p}{uwaga}")


def wizualizuj_wynik(warstwy, pojemnosci, przeplyw, wartosc, etykiety=None):
    _fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(max(14, 4.0 * len(warstwy)), 5.6))
    c_f = siec_rezydualna(pojemnosci, przeplyw)
    wizualizuj_siec(
        warstwy, pojemnosci, przeplyw=przeplyw, etykiety=etykiety,
        tytul=f"Przepływ maksymalny |f_max| = {wartosc}", ax=ax1,
    )
    wizualizuj_siec(
        warstwy, c_f, etykiety=etykiety,
        tytul="Końcowa sieć rezydualna G_f", rezydualna=True, ax=ax2,
    )
    plt.tight_layout()
    plt.show()