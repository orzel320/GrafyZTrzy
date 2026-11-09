"""Zadanie 2: Dijkstra zapisany zwykłymi pętlami, zgodnie z alg_3.pdf."""

from z3_zad1 import sprawdz_graf  # Wspólne sprawdzanie macierzy.


def init(n, s):
    """Ustaw początkowe odległości i poprzedników — algorytm 1 z PDF."""
    d = [float("inf")] * n  # Na początku nie znamy dróg do wierzchołków.
    poprzednik = [None] * n  # None oznacza brak poprzednika, czyli NIL.
    d[s] = 0  # Odległość źródła od siebie wynosi zero.
    return d, poprzednik  # Zwracamy dwie zwykłe listy.


def relax(u, v, w, d, poprzednik):
    """Popraw drogę do v, jeśli droga przez u jest krótsza — algorytm 2."""
    if d[v] > d[u] + w[u][v]:  # Porównujemy starą długość z nową.
        d[v] = d[u] + w[u][v]  # Zapamiętujemy krótszą odległość.
        poprzednik[v] = u  # Ostatni krok nowej drogi prowadzi z u.


def dijkstra(w, s):
    """Zwróć długości dróg i poprzedników. W kodzie numery zaczynają się od 0."""
    sprawdz_graf(w)  # Błędne wagi lub kształt macierzy dają czytelny błąd.
    n = len(w)  # Liczba wierzchołków.
    if type(s) is not int or s < 0 or s >= n:  # Zakaz indeksu spoza grafu.
        raise ValueError("Niepoprawny wierzchołek startowy.")
    d, poprzednik = init(n, s)  # Inicjalizacja zgodna z PDF.
    gotowy = [False] * n  # Tablica oznacza przynależność do zbioru S.
    for krok in range(n):  # Najwyżej n razy wybierzemy kolejny wierzchołek.
        u = -1  # Jeszcze nie wybrano żadnego wierzchołka.
        najmniejsza = float("inf")  # Szukamy najmniejszej skończonej odległości.
        for v in range(n):  # Zwykłe przeszukanie listy zamiast kopca.
            if not gotowy[v] and d[v] < najmniejsza:
                najmniejsza = d[v]  # Nowa najmniejsza znaleziona odległość.
                u = v  # Zapamiętujemy odpowiadający jej wierzchołek.
        if u == -1:  # Pozostałe wierzchołki są nieosiągalne.
            break  # Ich odległości pozostają nieskończone.
        gotowy[u] = True  # Odległość do u jest już ostateczna.
        for v in range(n):  # Sprawdzamy sąsiadów u.
            if w[u][v] > 0 and not gotowy[v]:  # Tylko krawędzie do niegotowych wierzchołków.
                relax(u, v, w, d, poprzednik)  # Wspólna funkcja z pseudokodu.
    return d, poprzednik  # Dane do wypisania długości i dróg.


def odtworz_sciezke(poprzednik, s, cel):
    """Przyjmuje tablicę poprzedników z Dijkstry uruchomionej dla źródła s."""
    droga = []  # Początkowo zbieramy drogę od końca.
    v = cel  # Zaczynamy w wierzchołku docelowym.
    while v is not None:  # Idziemy po kolejnych poprzednikach.
        droga.append(v)  # Dodajemy aktualny wierzchołek.
        if v == s:  # Dotarliśmy do źródła.
            droga.reverse()  # Ustawiamy kolejność od źródła do celu.
            return droga  # Gotowa najkrótsza droga.
        v = poprzednik[v]  # Cofamy się o jedną krawędź.
    return []  # Nie dotarliśmy do źródła: ścieżka nie istnieje.


def wypisz_sciezki(w, s):
    """Wypisz jedną najkrótszą drogę do każdego wierzchołka, jak w PDF."""
    d, poprzednik = dijkstra(w, s)  # Jeden przebieg znajduje wszystkie długości.
    for cel in range(len(w)):  # Uwzględniamy też samo źródło.
        droga = odtworz_sciezke(poprzednik, s, cel)  # Odtwarzamy konkretną drogę.
        if droga == []:  # Brak połączenia ze źródłem.
            print("Do", cel + 1, ": brak ścieżki, odległość = inf")
        else:  # Zamieniamy indeksy na numery prezentowane od 1.
            numery = []  # Osobna lista do wypisania.
            for v in droga:
                numery.append(v + 1)  # W kodzie 0..n-1, na ekranie 1..n.
            print("Do", cel + 1, ":", numery, "długość =", d[cel])
