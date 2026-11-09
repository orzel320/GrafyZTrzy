import random 
import runpy  
import matplotlib.pyplot as plt  
import networkx as nx  
from matplotlib.transforms import Bbox  
from pathlib import Path  
from zad3 import generuj_gnp  
from zestaw2.z2 import get_components  

stary_kod = runpy.run_path(str(Path(__file__).with_name("zad1-2.py")))
konwertuj = stary_kod["konwertuj"]  
wypisz_macierz = stary_kod["wypisz_macierz"] 


def sprawdz_graf(w):
    """Sprawdź macierz przed obliczeniami. Nie wymaga spójności."""
    if not isinstance(w, list) or len(w) == 0:  
        raise ValueError("Graf musi mieć przynajmniej jeden wierzchołek.")
    n = len(w)  
    for wiersz in w:  
        if not isinstance(wiersz, list) or len(wiersz) != n:
            raise ValueError("Macierz musi być kwadratowa.")
    for u in range(n):  
        for v in range(n):  
            if type(w[u][v]) is not int or w[u][v] < 0:  
                raise ValueError("W macierzy mogą być tylko nieujemne liczby całkowite.")
            if u == v and w[u][v] != 0:  
                raise ValueError("Na przekątnej muszą być zera.")
            if w[u][v] != w[v][u]:  
                raise ValueError("Macierz musi być symetryczna.")


def generuj_graf(n, p):
    """Wylosuj graf starym kodem, połącz jego składowe i nadaj wagi."""
    if type(n) is not int or n < 1:  
        raise ValueError("Liczba wierzchołków musi być całkowita i dodatnia.")
    if type(p) not in (int, float) or not 0 <= p <= 1:  
        raise ValueError("Prawdopodobieństwo musi należeć do [0, 1].")
    krawedzie = generuj_gnp(n, p)  
    w, macierz_incydencji, lista = konwertuj(n, krawedzie)  
    sasiedzi = {}  
    for u in range(n):  
        sasiedzi[u] = lista[u]  
    skladowe = get_components(sasiedzi)  
    for i in range(1, len(skladowe)):  
        u = random.choice(skladowe[i - 1])  
        v = random.choice(skladowe[i])  
        w[u][v] = 1  
        w[v][u] = 1  
    for u in range(n):  
        for v in range(u + 1, n):  
            if w[u][v] != 0:  
                waga = random.randint(1, 10)  
                w[u][v] = waga  
                w[v][u] = waga  
    return w  


def rozmiesc_wagi(graf, polozenia, osie):
    """Umieść wagi bez nakładania napisów; zwróć te, które nie zmieściły się."""
    figura = osie.figure  
    figura.canvas.draw()  
    renderer = figura.canvas.get_renderer() 
    zajete = []  
    punkty = {}
    promien = 22 * figura.dpi / 100  
    for v in graf.nodes():
        x, y = osie.transData.transform(polozenia[v])
        punkty[v] = (x, y)
        zajete.append(Bbox.from_bounds(x - promien, y - promien, 2 * promien, 2 * promien))
    brak_miejsca = []  
    for u, v, dane in graf.edges(data=True):
        napis = osie.text(0, 0, str(dane["weight"]), ha="center", va="center",
                          fontsize=10, zorder=5,
                          bbox=dict(facecolor="white", edgecolor="none", pad=1.5))
        najlepsze = None 
        najlepszy_odstep = -1 
        for krok in range(6, 35):  
            t = krok / 40  
            x = (1 - t) * polozenia[u][0] + t * polozenia[v][0]
            y = (1 - t) * polozenia[u][1] + t * polozenia[v][1]
            napis.set_position((x, y))  
            prostokat = napis.get_window_extent(renderer).padded(4 * figura.dpi / 100)
            kolizja = False
            for inny in zajete:
                if prostokat.overlaps(inny):  
                    kolizja = True
                    break
            if kolizja:
                continue  
            px, py = osie.transData.transform((x, y))
            odstep = float("inf")
            for a, b in graf.edges():  
                if (a, b) == (u, v):
                    continue  
                ax, ay = punkty[a]
                bx, by = punkty[b]
                dx, dy = bx - ax, by - ay
                dlugosc2 = dx * dx + dy * dy  
                rzut = 0
                if dlugosc2 > 0:
                    rzut = ((px - ax) * dx + (py - ay) * dy) / dlugosc2
                rzut = max(0, min(1, rzut))  
                odleglosc2 = (px - ax - rzut * dx) ** 2 + (py - ay - rzut * dy) ** 2
                odstep = min(odstep, odleglosc2) 
            if najlepsze is None or odstep > najlepszy_odstep:
                najlepsze = (x, y)
                najlepszy_odstep = odstep
        if najlepsze is None:  
            napis.remove()
            brak_miejsca.append((u + 1, v + 1, dane["weight"]))
        else:
            napis.set_position(najlepsze)
            zajete.append(napis.get_window_extent(renderer).padded(4 * figura.dpi / 100))
    return brak_miejsca 


def wizualizuj_graf(w, tytul="Zadanie 1: graf z wagami", drzewo=None):
    """Otwórz okno z grafem; po podaniu drzewa rysuj tylko jego krawędzie."""
    sprawdz_graf(w)  
    n = len(w) 
    graf = nx.Graph() 
    graf.add_nodes_from(range(n))
    if drzewo is None:  
       for u in range(n):
            for v in range(u + 1, n):  
                if w[u][v] > 0:
                    graf.add_edge(u, v, weight=w[u][v])  
    else:  
        for u, v, waga in drzewo:
            graf.add_edge(u, v, weight=waga)
    polozenia = nx.circular_layout(graf)  
    podpisy = {}  
    for v in range(n):
        podpisy[v] = v + 1
    kolor = "gray"  
    if drzewo is not None:
        kolor = "royalblue"
    plt.figure(figsize=(10, 10))  
    osie = plt.gca()  
    nx.draw_networkx(graf, polozenia, labels=podpisy, node_color="skyblue",
                     node_size=650, edgecolors="black", edge_color=kolor,
                     width=2, font_size=11) 
    plt.title(tytul)  
    plt.axis("off")  
    plt.margins(0.15)  
    plt.tight_layout()  
    plt.subplots_adjust(top=0.90)  
    brak_miejsca = rozmiesc_wagi(graf, polozenia, osie)  
    if brak_miejsca:
        osie.set_title(tytul + "\nCzęść wag w dodatkowym oknie: lista krawędzi", fontsize=11)
        for poczatek in range(0, len(brak_miejsca), 25):  
            plt.figure(figsize=(6, 8))
            plt.axis("off")
            plt.title("Wagi bez miejsca na rysunku — strona " + str(poczatek // 25 + 1))
            tekst = "Krawędź       Waga\n\n"
            for u, v, waga in brak_miejsca[poczatek:poczatek + 25]:
                tekst += str(u) + " -- " + str(v) + "          " + str(waga) + "\n"
            plt.text(0.05, 0.95, tekst, va="top", fontsize=12, transform=plt.gca().transAxes)
            plt.tight_layout()
    plt.show() 
