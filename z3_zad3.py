"""Zadanie 3: odległości między każdą parą wierzchołków."""

from z3_zad1 import sprawdz_graf  # Ten sam sposób kontroli danych.
from z3_zad2 import dijkstra  # Nie przepisujemy algorytmu z poprzedniego zadania.


def macierz_odleglosci(w):
    sprawdz_graf(w)  # Odrzucamy też pusty graf.
    macierz = []  # Tutaj zbierzemy kolejne wiersze wyniku.
    for s in range(len(w)):  # Każdy wierzchołek zostaje raz źródłem.
        d, poprzednik = dijkstra(w, s)  # Wykorzystujemy zadanie 2.
        macierz.append(d)  # Odległości od s tworzą wiersz s.
    return macierz  # Wynik jest zwykłą listą list.
