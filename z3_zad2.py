
from z3_zad1 import sprawdz_graf  


def init(n, s):
    d = [float("inf")] * n 
    poprzednik = [None] * n  
    d[s] = 0  
    return d, poprzednik 


def relax(u, v, w, d, poprzednik):
    if d[v] > d[u] + w[u][v]:  
        d[v] = d[u] + w[u][v]  
        poprzednik[v] = u  


def dijkstra(w, s):
    sprawdz_graf(w)  
    n = len(w) 
    if type(s) is not int or s < 0 or s >= n:  
        raise ValueError("Niepoprawny wierzchołek startowy.")
    d, poprzednik = init(n, s)
    gotowy = [False] * n  
    for krok in range(n):  
        u = -1  
        najmniejsza = float("inf")  
        for v in range(n):  
            if not gotowy[v] and d[v] < najmniejsza:
                najmniejsza = d[v]  
                u = v  
        if u == -1:  
            break  
        gotowy[u] = True  
        for v in range(n):  
            if w[u][v] > 0 and not gotowy[v]:  
                relax(u, v, w, d, poprzednik)  
    return d, poprzednik  


def odtworz_sciezke(poprzednik, s, cel):
    droga = []  
    v = cel  
    while v is not None:
        droga.append(v)  
        if v == s:  
            droga.reverse()  
            return droga  
        v = poprzednik[v]  
    return []  


def wypisz_sciezki(w, s):
    d, poprzednik = dijkstra(w, s)  
    for cel in range(len(w)): 
        droga = odtworz_sciezke(poprzednik, s, cel)  
        if droga == []:  
            print("Do", cel + 1, ": brak ścieżki, odległość = inf")
        else:
            numery = [] 
            for v in droga:
                numery.append(v + 1)
            print("Do", cel + 1, ":", numery, "długość =", d[cel])
