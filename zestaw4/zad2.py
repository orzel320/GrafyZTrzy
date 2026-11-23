import sys
import matplotlib.pyplot as plt
from zad1 import waliduj_digraf


def zbuduj_liste_sasiedztwa(n, luki):
    sasiedzi = [[] for _ in range(n)]
    for u, v in luki:
        sasiedzi[u].append(v)
    for lista in sasiedzi:
        lista.sort()
    return sasiedzi


def kosaraju(n, luki):
    luki = waliduj_digraf(n, luki, dozwolone_petle=True)
    if n + 100 > sys.getrecursionlimit():
        sys.setrecursionlimit(n + 100)

    graf = zbuduj_liste_sasiedztwa(n, luki)
    luki_transponowane = [(v, u) for u, v in luki]
    graf_transponowany = zbuduj_liste_sasiedztwa(n, luki_transponowane)

    odwiedzeni = set()
    kolejnosc_wyjscia = []

    def dfs_czas_wyjscia(v):
        odwiedzeni.add(v)
        for sasiad in graf[v]:
            if sasiad not in odwiedzeni:
                dfs_czas_wyjscia(sasiad)
        kolejnosc_wyjscia.append(v)

    for v in range(n):
        if v not in odwiedzeni:
            dfs_czas_wyjscia(v)

    odwiedzeni.clear()
    skladowe = []

    def dfs_skladowa(v, skladowa):
        odwiedzeni.add(v)
        skladowa.append(v)
        for sasiad in graf_transponowany[v]:
            if sasiad not in odwiedzeni:
                dfs_skladowa(sasiad, skladowa)

    for v in reversed(kolejnosc_wyjscia):
        if v not in odwiedzeni:
            skladowa = []
            dfs_skladowa(v, skladowa)
            skladowe.append(sorted(skladowa))

    return sorted(skladowe)


def czy_silnie_spojny(n, luki):
    return len(kosaraju(n, luki)) == 1


def kolory_skladowych(n, skladowe):
    kolory = ["#c6d9ff"] * n
    mapa = plt.get_cmap("Set3")
    for indeks, skladowa in enumerate(skladowe):
        kolor = mapa(indeks % mapa.N)
        for v in skladowa:
            kolory[v] = kolor
    return kolory


def wypisz_skladowe(skladowe, od_jedynki=True):
    if not skladowe:
        print("Brak składowych (digraf pusty).")
        return
    baza = 1 if od_jedynki else 0
    for i, skladowa in enumerate(skladowe, start=1):
        wierzcholki = ", ".join(str(v + baza) for v in skladowa)
        print(f"Składowa {i}: {{{wierzcholki}}}")