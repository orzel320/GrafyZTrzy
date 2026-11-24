"""
- zadanie 1: obie metody PageRank dla digrafu przykładowego z instrukcji,
- zadanie 2: symulowane wyżarzanie dla pliku xqf131.dat.
"""
from __future__ import annotations
import argparse
import math
import random
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt


# Zadanie 1. PageRank

GRAPH = {
    "A": ["E", "F", "I"],
    "B": ["A", "C", "F"],
    "C": ["B", "D", "E", "L"],
    "D": ["C", "E", "H", "I", "K"],
    "E": ["C", "G", "H", "I"],
    "F": ["B", "G"],
    "G": ["E", "F", "H"],
    "H": ["D", "G", "I", "L"],
    "I": ["D", "E", "H", "J"],
    "J": ["I"],
    "K": ["D", "I"],
    "L": ["A", "H"],
}


def pagerank_power(graph=GRAPH, d=0.15, tol=1e-12, max_iter=10000):
    nodes = list(graph)
    n = len(nodes)
    index = {v: i for i, v in enumerate(nodes)}
    P = np.full((n, n), d / n, dtype=float)

    for u, neighbors in graph.items():
        if not neighbors:
            raise ValueError(f"Wierzchołek {u} nie ma krawędzi wychodzących.")
        i = index[u]
        for v in neighbors:
            P[i, index[v]] += (1.0 - d) / len(neighbors)

    p = np.full(n, 1.0 / n)
    for iteration in range(1, max_iter + 1):
        new_p = p @ P
        if np.linalg.norm(new_p - p, ord=1) < tol:
            p = new_p
            break
        p = new_p
    else:
        iteration = max_iter
    return {v: float(p[index[v]]) for v in nodes}, iteration


def pagerank_random_walk(graph=GRAPH, d=0.15, steps=1_000_000, seed=42):
    rng = random.Random(seed)
    nodes = list(graph)
    n = len(nodes)
    current = rng.randrange(n)
    visits = [0] * n
    index = {v: i for i, v in enumerate(nodes)}
    for _ in range(steps):
        visits[current] += 1
        if rng.random() < d:
            current = rng.randrange(n)
        else:
            current = index[rng.choice(graph[nodes[current]])]
    return {v: visits[i] / steps for i, v in enumerate(nodes)}


def print_ranking(title, ranking):
    print("\n" + title)
    for place, (node, score) in enumerate(
        sorted(ranking.items(), key=lambda item: item[1], reverse=True), 1
    ):
        print(f"{place:2}. {node}  PageRank = {score:.6f}")


# Zadanie 2. TSP – symulowane wyżarzanie + ruch 2-opt

def cycle_length(route, coords):
    points = coords[np.asarray(route, dtype=int)]
    return float(np.linalg.norm(points - np.roll(points, -1, axis=0), axis=1).sum())


def two_opt_annealing(coords, initial_route=None, levels=100, iterations=3000,
                      t_start=20.0, t_end=0.03, seed=42):
    rng = random.Random(seed)
    n = len(coords)
    route = list(range(n)) if initial_route is None else list(initial_route)
    if len(route) != n or set(route) != set(range(n)):
        raise ValueError("Trasa początkowa musi być permutacją indeksów 0..n-1.")

    current_len = cycle_length(route, coords)
    best_route = route.copy()
    best_len = current_len

    for level in range(levels):
        # Chłodzenie geometryczne od t_start do t_end.
        fraction = level / max(1, levels - 1)
        temperature = t_start * (t_end / t_start) ** fraction

        for _ in range(iterations):
            i, j = sorted((rng.randrange(n), rng.randrange(n)))
            # Krawędzie muszą być różne i niesąsiednie.
            if i == j or j == i + 1 or (i == 0 and j == n - 1):
                continue

            a, b = route[i], route[(i + 1) % n]
            c, d = route[j], route[(j + 1) % n]

            # Zmiana długości liczona tylko dla 4 zmienianych krawędzi.
            delta = (
                np.linalg.norm(coords[a] - coords[c])
                + np.linalg.norm(coords[b] - coords[d])
                - np.linalg.norm(coords[a] - coords[b])
                - np.linalg.norm(coords[c] - coords[d])
            )

            # Kryterium Metropolisa-Hastingsa.
            if delta < 0 or rng.random() < math.exp(-delta / temperature):
                route[i + 1:j + 1] = reversed(route[i + 1:j + 1])
                current_len += float(delta)
                if current_len < best_len:
                    best_len = current_len
                    best_route = route.copy()

    return best_route, best_len


def plot_tour(coords, route, filename, title):
    ordered = coords[np.asarray(route, dtype=int)]
    closed = np.vstack((ordered, ordered[0]))
    plt.figure(figsize=(8, 5))
    plt.plot(closed[:, 0], closed[:, 1], "-o", markersize=3, linewidth=0.8)
    plt.scatter(coords[:, 0], coords[:, 1], s=10)
    plt.xlabel("x")
    plt.ylabel("y")
    plt.title(title)
    plt.axis("equal")
    plt.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(filename, dpi=180)
    plt.close()


def solve_tsp(data_file, restarts=5, levels=100, iterations=3000, seed=42):
    data_path = Path(data_file)
    if not data_path.exists():
        data_path = Path(__file__).resolve().parent / data_file
    coords = np.loadtxt(data_path, dtype=float)
    if coords.ndim != 2 or coords.shape[1] != 2:
        raise ValueError("Plik z punktami musi zawierać dokładnie dwie kolumny.")
    n = len(coords)
    initial = list(range(n))
    initial_len = cycle_length(initial, coords)

    best_route, best_len = None, float("inf")
    for run in range(restarts):
        route, length = two_opt_annealing(
            coords, initial_route=initial, levels=levels,
            iterations=iterations, seed=seed + run
        )
        print(f"Uruchomienie {run + 1}/{restarts}: długość = {length:.3f}")
        if length < best_len:
            best_route, best_len = route, length

    plot_tour(coords, initial, "cykl_poczatkowy.png",
              f"Cykl początkowy, długość = {initial_len:.3f}")
    plot_tour(coords, best_route, "cykl_wynikowy.png",
              f"Cykl po wyżarzaniu, długość = {best_len:.3f}")
    np.savetxt("cykl_wynikowy.txt", np.asarray(best_route, dtype=int), fmt="%d")
    print(f"\nLiczba wierzchołków: {n}")
    print(f"Długość cyklu początkowego: {initial_len:.3f}")
    print(f"Najlepsza znaleziona długość: {best_len:.3f}")
    print("Zapisano: cykl_poczatkowy.png, cykl_wynikowy.png, cykl_wynikowy.txt")


def main():
    parser = argparse.ArgumentParser(description="Rozwiązanie zestawu 6.")
    parser.add_argument("--data", default="xqf131.dat",
                        help="Ścieżka do pliku współrzędnych TSP.")
    parser.add_argument("--restarts", type=int, default=5)
    parser.add_argument("--levels", type=int, default=100)
    parser.add_argument("--iterations", type=int, default=3000)
    parser.add_argument("--walk-steps", type=int, default=1_000_000)
    args = parser.parse_args()

    walk = pagerank_random_walk(steps=args.walk_steps)
    power, count = pagerank_power()
    print_ranking("PageRank – błądzenie przypadkowe", walk)
    print_ranking(f"PageRank – metoda potęgowa (zbieżność po {count} iteracjach)", power)

    print("\nPorównanie metod PageRank:")
    for node in GRAPH:
        print(f"{node}: błądzenie={walk[node]:.6f}, metoda potęgowa={power[node]:.6f}")

    solve_tsp(args.data, restarts=args.restarts,
              levels=args.levels, iterations=args.iterations)


if __name__ == "__main__":
    main()
