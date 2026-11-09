"""Uruchom ten plik. Jeden wylosowany graf jest wspólny dla wszystkich zadań."""

from z3_zad1 import generuj_graf, wypisz_macierz, wizualizuj_graf  # Zadanie 1 i prezentacja.
from z3_zad2 import wypisz_sciezki  # Zadanie 2.
from z3_zad3 import macierz_odleglosci  # Zadanie 3.
from z3_zad4 import wypisz_centra  # Zadanie 4.
from z3_zad5 import wypisz_drzewo  # Zadanie 5.


def main():
    try:  # Błędne dane wejściowe pokażemy jako krótki komunikat.
        n = int(input("Liczba wierzchołków: "))
        p = float(input("Prawdopodobieństwo krawędzi: "))
        w = generuj_graf(n, p)  # Losowanie następuje tylko raz.
    except ValueError as blad:
        print("Błąd:", blad)
        return  # Bez poprawnego grafu nie przechodzimy do menu.

    odleglosci = None  # Macierz obliczymy dopiero przy zadaniu 3 lub 4.
    while True:  # Kolejne zadania korzystają z tej samej macierzy wag w.
        print("\n1 - graf z wagami")
        print("2 - najkrótsze ścieżki")
        print("3 - macierz odległości")
        print("4 - centrum i centrum minimax")
        print("5 - minimalne drzewo rozpinające")
        print("6 - wszystkie zadania")
        print("0 - koniec")
        wybor = input("Wybierz zadanie: ").strip()
        if wybor == "0":
            break  # Kończymy program.
        if wybor not in ["1", "2", "3", "4", "5", "6"]:
            print("Wybierz liczbę od 0 do 6.")
            continue  # Ponownie pokazujemy menu.
        try:
            if wybor in ["1", "6"]:
                print("\nZADANIE 1: macierz wag (0 = brak krawędzi)")
                wypisz_macierz(w)
                wizualizuj_graf(w)  # Otwieramy okno; po jego zamknięciu program kontynuuje.
            if wybor in ["2", "6"]:
                s = int(input("Wierzchołek startowy (od 1 do " + str(n) + "): "))
                print("\nZADANIE 2: najkrótsze ścieżki")
                wypisz_sciezki(w, s - 1)  # Przeliczamy numer użytkownika na indeks listy.
            if wybor in ["3", "4", "6"] and odleglosci is None:
                odleglosci = macierz_odleglosci(w)  # Zadania 3 i 4 współdzielą wynik.
            if wybor in ["3", "6"]:
                print("\nZADANIE 3: macierz odległości")
                wypisz_macierz(odleglosci)
            if wybor in ["4", "6"]:
                print("\nZADANIE 4: centra")
                wypisz_centra(odleglosci)
            if wybor in ["5", "6"]:
                print("\nZADANIE 5: minimalne drzewo rozpinające")
                wypisz_drzewo(w)
        except ValueError as blad:
            print("Błąd:", blad)  # Wracamy do menu, zachowując ten sam graf.


if __name__ == "__main__":  # Import pliku nie uruchamia pytań do użytkownika.
    main()  # Rozpocznij program.
