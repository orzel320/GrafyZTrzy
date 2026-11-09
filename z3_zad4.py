"""Zadanie 4: centra na podstawie macierzy z zadania 3."""

import random  # Losowy wybór jednego spośród równorzędnych centrów minimax.

def centra(macierz):
    """Przyjmuje gotową macierz ODLEGŁOŚCI zwróconą przez zadanie 3."""
    if len(macierz) == 0:  # Pusty graf nie ma centrum.
        raise ValueError("Graf nie może być pusty.")
    sumy = []  # Suma odległości dla każdego wierzchołka.
    maksima = []  # Odległość do najdalszego wierzchołka.
    for wiersz in macierz:  # Każdy wiersz odpowiada jednemu źródłu.
        if float("inf") in wiersz:  # Wykrycie niespójności grafu.
            raise ValueError("Graf niespójny: nie wyznaczamy centrum.")
        sumy.append(sum(wiersz))  # Kryterium centrum sumacyjnego.
        maksima.append(max(wiersz))  # Kryterium centrum minimax.
    najmniejsza_suma = min(sumy)  # Najlepszy wynik pierwszego kryterium.
    najmniejsze_maksimum = min(maksima)  # Najlepszy wynik drugiego kryterium.
    centrum = []  # Zachowamy wszystkie remisy.
    minimax = []  # Tutaj także może być kilka wierzchołków.
    for v in range(len(macierz)):
        if sumy[v] == najmniejsza_suma:
            centrum.append(v + 1)  # Zwracamy numery gotowe do pokazania, od 1.
        if maksima[v] == najmniejsze_maksimum:
            minimax.append(v + 1)  # Numery minimax także od 1.
    return centrum, najmniejsza_suma, minimax, najmniejsze_maksimum


def wypisz_centra(macierz):
    centrum, suma, minimax, maksimum = centra(macierz)  # Rozpakowanie wyniku.
    wybrane = random.choice(minimax)  # Losujemy tylko spośród najlepszych wierzchołków.
    pozostale = []  # Pozostałe centra minimax nadal pokażemy użytkownikowi.
    for v in minimax:
        if v != wybrane:
            pozostale.append(v)
    print("Centrum:", centrum, "suma odległości:", suma)
    print("Wybrane losowo centrum minimax:", wybrane, "odległość do najdalszego:", maksimum)
    print("Wszystkie centra minimax:", minimax)
    if pozostale:
        print("Pozostałe równorzędne centra minimax:", pozostale)
    else:
        print("Brak innych centrów minimax.")  # Także przypadek jednego wierzchołka.
