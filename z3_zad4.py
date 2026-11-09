
import random  

def centra(macierz):
    if len(macierz) == 0:  
        raise ValueError("Graf nie może być pusty.")
    sumy = []  
    maksima = []  
    for wiersz in macierz:  
        if float("inf") in wiersz:  
            raise ValueError("Graf niespójny: nie wyznaczamy centrum.")
        sumy.append(sum(wiersz))  
        maksima.append(max(wiersz)) 
    najmniejsza_suma = min(sumy)  
    najmniejsze_maksimum = min(maksima)  
    centrum = []  
    minimax = []  
    for v in range(len(macierz)):
        if sumy[v] == najmniejsza_suma:
            centrum.append(v + 1)  
        if maksima[v] == najmniejsze_maksimum:
            minimax.append(v + 1) 
    return centrum, najmniejsza_suma, minimax, najmniejsze_maksimum


def wypisz_centra(macierz):
    centrum, suma, minimax, maksimum = centra(macierz) 
    wybrane = random.choice(minimax)  
    pozostale = []  
    for v in minimax:
        if v != wybrane:
            pozostale.append(v)
    print("Centrum:", centrum, "suma odległości:", suma)
    print("Wybrane losowo centrum minimax:", wybrane, "odległość do najdalszego:", maksimum)
    print("Wszystkie centra minimax:", minimax)
    if pozostale:
        print("Pozostałe równorzędne centra minimax:", pozostale)
    else:
        print("Brak innych centrów minimax.") 
