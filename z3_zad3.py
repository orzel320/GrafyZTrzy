
from z3_zad1 import sprawdz_graf  
from z3_zad2 import dijkstra 


def macierz_odleglosci(w):
    sprawdz_graf(w)
    macierz = []  
    for s in range(len(w)):  
        d, poprzednik = dijkstra(w, s)  
        macierz.append(d) 
    return macierz  
