
from z3_zad1 import sprawdz_graf, wizualizuj_graf  


def prim(w):
    sprawdz_graf(w)  
    n = len(w)  
    w_drzewie = [False] * n  
    koszt = [float("inf")] * n 
    rodzic = [None] * n  
    koszt[0] = 0  
    drzewo = [] 
    suma = 0 
    for krok in range(n):  
        u = -1  
        minimum = float("inf")  
        for v in range(n):  
            if not w_drzewie[v] and koszt[v] < minimum:
                minimum = koszt[v]
                u = v  
        if u == -1:  
            raise ValueError("Graf niespójny: drzewo rozpinające nie istnieje.")
        w_drzewie[u] = True  # dolaczamy wierzcholek do T
        if rodzic[u] is not None:  
            drzewo.append((rodzic[u], u, koszt[u]))  
            suma += koszt[u]  
        for v in range(n):  
            if w[u][v] > 0 and not w_drzewie[v]:  
                if w[u][v] < koszt[v]:  
                    koszt[v] = w[u][v]  
                    rodzic[v] = u  
    return drzewo, suma  


def wypisz_drzewo(w):
    drzewo, suma = prim(w)  
    for u, v, waga in drzewo: 
        print(u + 1, "--", v + 1, "waga:", waga)  
    print("Suma wag drzewa:", suma)
    wizualizuj_graf(w, "Zadanie 5: minimalne drzewo, suma wag = " + str(suma), drzewo)
