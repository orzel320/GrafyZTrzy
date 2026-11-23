import math
import random
from zad1 import waliduj_digraf, generuj_digraf_gnp
from zad2 import czy_silnie_spojny


class CyklUjemnyError(ValueError):
    pass


def waliduj_digraf_wazony(n, wagi, dozwolone_petle=True):
    waliduj_digraf(n, list(wagi.keys()), dozwolone_petle=dozwolone_petle)
    for luk, w in wagi.items():
        if not isinstance(w, (int, float)) or isinstance(w, bool) or not math.isfinite(w):
            raise ValueError(f"Waga łuku {luk} musi być skończoną liczbą.")
    return wagi


def _parsuj_wage(token):
    try:
        return int(token)
    except ValueError:
        wartosc = float(token)
        if not math.isfinite(wartosc):
            raise ValueError(f"Niepoprawna waga: {token}")
        return wartosc


def wczytaj_digraf_wazony(nazwa, od_jedynki=True, dozwolone_petle=True):
    with open(nazwa, "r", encoding="utf-8") as f:
        linie = [l.split("#", 1)[0].strip() for l in f]
        linie = [l for l in linie if l]

    if not linie:
        raise ValueError("Plik jest pusty.")
    if linie == ["0"]:
        return 0, {}

    pierwsza = linie[0].split()
    baza = 1 if od_jedynki else 0

    # 1. Lista łuków ważonych: "n m", potem m wierszy "u v w"
    if len(pierwsza) == 2 and all(t.isdigit() for t in pierwsza):
        n, m = int(pierwsza[0]), int(pierwsza[1])
        if len(linie) != m + 1:
            raise ValueError(f"Zadeklarowano {m} łuków, ale znaleziono {len(linie) - 1}.")
        wagi = {}
        for linia in linie[1:]:
            tok = linia.split()
            if len(tok) != 3:
                raise ValueError(f"Niepoprawny wiersz łuku: '{linia}'. Oczekiwano 'u v w'.")
            luk = (int(tok[0]) - baza, int(tok[1]) - baza)
            if luk in wagi:
                raise ValueError(f"Powtórzony łuk: {luk}.")
            wagi[luk] = _parsuj_wage(tok[2])
        return n, waliduj_digraf_wazony(n, wagi, dozwolone_petle=dozwolone_petle)

    # 2. Macierz wag n x n (brak łuku oznaczony przez '.' lub 'inf')
    n = len(linie)
    wagi = {}
    for i, linia in enumerate(linie):
        tok = linia.split()
        if len(tok) != n:
            raise ValueError("Niepoprawny format pliku: oczekiwano 'n m' + 'u v w' lub macierzy n x n.")
        for j, pole in enumerate(tok):
            if pole.lower() not in (".", "inf", "∞"):
                wagi[(i, j)] = _parsuj_wage(pole)

    return n, waliduj_digraf_wazony(n, wagi, dozwolone_petle=dozwolone_petle)


def generuj_silnie_spojny_digraf(n, p, max_prob=10000, seed=None):
    if not isinstance(n, int) or isinstance(n, bool) or n <= 0:
        raise ValueError("Silnie spójny digraf musi mieć co najmniej 1 wierzchołek (n >= 1).")
    if n >= 2 and p == 0:
        raise ValueError("Dla n >= 2 i p = 0 nie istnieje silnie spójny digraf.")

    rng = random.Random(seed)
    for _ in range(max_prob):
        luki = generuj_digraf_gnp(n, p, seed=rng.randrange(2**32))
        if czy_silnie_spojny(n, luki):
            return luki

    raise RuntimeError(
        f"Nie udało się wylosować silnie spójnego digrafu G({n}, {p}) w {max_prob} próbach."
    )


def losuj_wagi(luki, min_w=-5, max_w=10, seed=None):
    if min_w > max_w:
        raise ValueError("min_w nie może być większe niż max_w.")
    rng = random.Random(seed)
    return {luk: rng.randint(min_w, max_w) for luk in luki}


def generuj_silnie_spojny_wazony(
    n, p, min_w=-5, max_w=10, bez_cyklu_ujemnego=False, max_prob_wag=500, seed=None
):
    rng = random.Random(seed)
    luki = generuj_silnie_spojny_digraf(n, p, seed=rng.randrange(2**32))

    if not bez_cyklu_ujemnego:
        return losuj_wagi(luki, min_w, max_w, seed=rng.randrange(2**32))

    for _ in range(max_prob_wag):
        wagi = losuj_wagi(luki, min_w, max_w, seed=rng.randrange(2**32))
        try:
            bellman_ford(n, wagi, start=0)
            return wagi
        except CyklUjemnyError:
            continue

    raise RuntimeError(
        f"Nie udało się wylosować wag z [{min_w}, {max_w}] bez cyklu ujemnego w {max_prob_wag} próbach."
    )


def bellman_ford(n, wagi, start):
    waliduj_digraf_wazony(n, wagi, dozwolone_petle=True)
    if not isinstance(start, int) or isinstance(start, bool) or not 0 <= start < n:
        raise ValueError(f"Wierzchołek startowy {start} poza zakresem [0, {n - 1}].")

    odleglosci = [math.inf] * n
    poprzednicy = [None] * n
    odleglosci[start] = 0

    for _ in range(n - 1):
        zmiana = False
        for (u, v), w in wagi.items():
            if odleglosci[u] != math.inf and odleglosci[u] + w < odleglosci[v]:
                odleglosci[v] = odleglosci[u] + w
                poprzednicy[v] = u
                zmiana = True
        if not zmiana:
            break

    for (u, v), w in wagi.items():
        if odleglosci[u] != math.inf and odleglosci[u] + w < odleglosci[v]:
            raise CyklUjemnyError(
                f"Wykryto cykl o ujemnej sumie wag osiągalny z wierzchołka {start}."
            )

    return odleglosci, poprzednicy


def odtworz_sciezke(poprzednicy, start, cel):
    if start == cel:
        return [start]
    if poprzednicy[cel] is None:
        return None
    sciezka = []
    aktualny = cel
    while aktualny is not None:
        sciezka.append(aktualny)
        if aktualny == start:
            return list(reversed(sciezka))
        aktualny = poprzednicy[aktualny]
    return None


def wypisz_sciezki(start, odleglosci, poprzednicy, od_jedynki=True):
    baza = 1 if od_jedynki else 0
    for cel, d in enumerate(odleglosci):
        if d == math.inf:
            print(f"{start + baza} -> {cel + baza}: brak ścieżki (∞)")
        else:
            sciezka = odtworz_sciezke(poprzednicy, start, cel)
            trasa = " -> ".join(str(v + baza) for v in sciezka)
            print(f"{start + baza} -> {cel + baza}: koszt = {d:>3}, ścieżka: {trasa}")