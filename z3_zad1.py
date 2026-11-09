import random  # Losowanie końców mostów i wag.
import runpy  # Pozwala użyć pliku, który ma myślnik w nazwie.
import matplotlib.pyplot as plt  # Okienko z rysunkiem, tak jak w zestawie 1.
import networkx as nx  # Tylko rozmieszczenie i rysowanie grafu, nie obliczanie wyników.
from pathlib import Path  # Znalezienie starego pliku obok tego programu.
from zad3 import generuj_gnp  # Oryginalny generator z pierwszego zestawu.
from zestaw2.z2 import get_components  # Oryginalne znajdowanie składowych.

# Zwykły import nie obsługuje nazwy zad1-2, dlatego ten jeden plik ładujemy tak.
stary_kod = runpy.run_path(str(Path(__file__).with_name("zad1-2.py")))
konwertuj = stary_kod["konwertuj"]  # Nie piszemy ponownie konwersji krawędzi.
wypisz_macierz = stary_kod["wypisz_macierz"]  # Nie powielamy drukowania macierzy.


def sprawdz_graf(w):
    """Sprawdź macierz przed obliczeniami. Nie wymaga spójności."""
    if not isinstance(w, list) or len(w) == 0:  # Pusty graf nie ma centrum ani źródła.
        raise ValueError("Graf musi mieć przynajmniej jeden wierzchołek.")
    n = len(w)  # Liczba wierszy jest liczbą wierzchołków.
    for wiersz in w:  # Najpierw sprawdzamy rozmiary wszystkich wierszy.
        if not isinstance(wiersz, list) or len(wiersz) != n:
            raise ValueError("Macierz musi być kwadratowa.")
    for u in range(n):  # Przeglądamy każdy wiersz.
        for v in range(n):  # Przeglądamy każdą kolumnę.
            if type(w[u][v]) is not int or w[u][v] < 0:  # bool także jest odrzucany.
                raise ValueError("W macierzy mogą być tylko nieujemne liczby całkowite.")
            if u == v and w[u][v] != 0:  # Graf prosty nie ma pętli.
                raise ValueError("Na przekątnej muszą być zera.")
            if w[u][v] != w[v][u]:  # Waga musi być jednakowa w obu kierunkach.
                raise ValueError("Macierz musi być symetryczna.")


def generuj_graf(n, p):
    """Wylosuj graf starym kodem, połącz jego składowe i nadaj wagi."""
    if type(n) is not int or n < 1:  # Obsługujemy również n=1.
        raise ValueError("Liczba wierzchołków musi być całkowita i dodatnia.")
    if type(p) not in (int, float) or not 0 <= p <= 1:  # Odrzuca także NaN i nieskończoność.
        raise ValueError("Prawdopodobieństwo musi należeć do [0, 1].")
    krawedzie = generuj_gnp(n, p)  # Ponowne użycie oryginalnego generatora.
    w, macierz_incydencji, lista = konwertuj(n, krawedzie)  # Stara konwersja daje macierz i sąsiadów.
    sasiedzi = {}  # Stary get_components oczekuje słownika.
    for u in range(n):  # Uwzględniamy także izolowane wierzchołki.
        sasiedzi[u] = lista[u]  # Nie implementujemy drugiego przeszukiwania grafu.
    skladowe = get_components(sasiedzi)  # Każda pozycja to osobna składowa.
    for i in range(1, len(skladowe)):  # Łączymy kolejne składowe w łańcuch.
        u = random.choice(skladowe[i - 1])  # Losowy wierzchołek poprzedniej składowej.
        v = random.choice(skladowe[i])  # Losowy wierzchołek następnej składowej.
        w[u][v] = 1  # Dodajemy most między składowymi.
        w[v][u] = 1  # Graf jest nieskierowany.
    for u in range(n):  # Nadajemy wagi wszystkim istniejącym krawędziom.
        for v in range(u + 1, n):  # Każdą krawędź losujemy tylko raz.
            if w[u][v] != 0:  # Zero oznacza brak krawędzi.
                waga = random.randint(1, 10)  # Obie granice przedziału są włączone.
                w[u][v] = waga  # Waga w jednym kierunku.
                w[v][u] = waga  # Ta sama waga w drugim kierunku.
    return w  # Zwykła lista list, bez klas ani dodatkowego obiektu grafu.


def wizualizuj_graf(w, tytul="Zadanie 1: graf z wagami", drzewo=None):
    """Otwórz okno z grafem; po podaniu drzewa rysuj tylko jego krawędzie."""
    sprawdz_graf(w)  # Korzystamy z tej samej kontroli macierzy.
    n = len(w)  # Zachowujemy także wierzchołek bez krawędzi przy n=1.
    graf = nx.Graph()  # Pomocniczy obiekt biblioteki służy wyłącznie do rysowania.
    graf.add_nodes_from(range(n))  # Wszystkie wierzchołki muszą być na rysunku.
    if drzewo is None:  # Zadanie 1: wszystkie krawędzie grafu.
        for u in range(n):
            for v in range(u + 1, n):  # Każda nieskierowana krawędź tylko raz.
                if w[u][v] > 0:
                    graf.add_edge(u, v, weight=w[u][v])  # Zapamiętujemy wagę do podpisu.
    else:  # Zadanie 5: tylko krawędzie znalezione przez nasz algorytm Prima.
        for u, v, waga in drzewo:
            graf.add_edge(u, v, weight=waga)
    polozenia = nx.circular_layout(graf)  # Układ na okręgu, jak w zestawie 1.
    podpisy = {}  # Na ekranie pokazujemy numery od 1.
    for v in range(n):
        podpisy[v] = v + 1
    wagi = nx.get_edge_attributes(graf, "weight")  # Podpisy krawędzi to ich wagi.
    kolor = "gray"  # Zwykły graf ma szare krawędzie.
    if drzewo is not None:
        kolor = "royalblue"  # Krawędzie drzewa wyróżniamy na niebiesko.
    plt.figure(figsize=(8, 8))  # Każde wywołanie tworzy nowe okno.
    nx.draw_networkx(graf, polozenia, labels=podpisy, node_color="skyblue",
                     node_size=650, edgecolors="black", edge_color=kolor,
                     width=2, font_size=11)  # Wierzchołki, numery i krawędzie.
    nx.draw_networkx_edge_labels(graf, polozenia, edge_labels=wagi,
                                font_size=10, rotate=False)  # Wagi obok krawędzi.
    plt.title(tytul)  # Nazwa zadania nad rysunkiem.
    plt.axis("off")  # Osie liczbowe nie są potrzebne do grafu.
    plt.margins(0.15)  # Zostawiamy miejsce wokół skrajnych wierzchołków.
    plt.tight_layout()  # Dopasowanie rysunku do okna.
    plt.show()  # Program czeka na zamknięcie okna, potem wraca do menu.
