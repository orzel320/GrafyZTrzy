import random
import copy
import os
import colorsys
import networkx as nx
import matplotlib.pyplot as plt

# funkcja wizualizujaca
def draw_graph(adj, title="Graf", node_colors=None):
    """Rysuje graf na podstawie listy sąsiedztwa w układzie okrągłym."""
    G = nx.Graph()
    for u in adj:
        for v in adj[u]:
            if u < v:
                G.add_edge(u, v)
                
    for u in adj:
        if u not in G:
            G.add_node(u)

    plt.figure(figsize=(6, 6))
    pos = nx.circular_layout(G)
    
    if node_colors is None:
        node_colors = ['lightblue'] * G.number_of_nodes()
        
    nodelist = sorted(G.nodes())
    nx.draw(G, pos, nodelist=nodelist, with_labels=True, node_color=node_colors, 
            node_size=700, font_size=12, font_weight='bold', edge_color='black', width=1.5)
    
    plt.title(title)
    plt.show()

def degree_seq(A):
    seq = sorted(A, reverse=True)
    while True:
        if all(x == 0 for x in seq):
            return True
        if seq[0] >= len(seq) or any(x < 0 for x in seq):
            return False
        n_edges = seq[0]
        seq[0] = 0
        for i in range(1, n_edges + 1):
            seq[i] -= 1
        seq.sort(reverse=True)

def construct_graph(degrees):
    n = len(degrees)
    nodes = [[degrees[i], i] for i in range(n)]
    adj = {i: set() for i in range(n)}
    
    while True:
        nodes.sort(key=lambda x: x[0], reverse=True)
        if all(x[0] == 0 for x in nodes):
            break
        deg, u = nodes[0]
        nodes[0][0] = 0
        for i in range(1, deg + 1):
            nodes[i][0] -= 1
            v = nodes[i][1]
            adj[u].add(v)
            adj[v].add(u)
    return adj

def randomize_graph(adj, num_swaps=100):
    edges = set()
    for u in adj:
        for v in adj[u]:
            if u < v:
                edges.add((u, v))
    edges = list(edges)
    m = len(edges)
    if m < 2:
        return adj

    for _ in range(num_swaps):
        i, j = random.sample(range(m), 2)
        (a, b), (c, d) = edges[i], edges[j]
        if random.choice([True, False]):
            c, d = d, c
        if a != d and b != c and d not in adj[a] and c not in adj[b]:
            adj[a].remove(b); adj[b].remove(a)
            adj[c].remove(d); adj[d].remove(c)
            adj[a].add(d); adj[d].add(a)
            adj[b].add(c); adj[c].add(b)
            edges[i] = (min(a, d), max(a, d))
            edges[j] = (min(b, c), max(b, c))

def get_components(adj):
    visited = set()
    components = []
    for node in sorted(adj.keys()):
        if node not in visited:
            comp = []
            stack = [node]
            visited.add(node)
            while stack:
                curr = stack.pop()
                comp.append(curr)
                for neighbor in sorted(adj[curr]):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        stack.append(neighbor)
            components.append(sorted(comp)) 
    return components

def is_connected(adj):
    comps = get_components(adj)
    active_comps = [c for c in comps if any(len(adj[v]) > 0 for v in c)]
    return len(active_comps) <= 1

def generate_random_eulerian_graph(n):
    if n < 3:
        raise ValueError(
            "Graf eulerowski musi mieć co najmniej 3 wierzchołki."
        )
    while True:
        max_deg = n - 1 if (n - 1) % 2 == 0 else n - 2
        degrees = [random.choice(range(2, max_deg + 1, 2)) for _ in range(n)]
        if degree_seq(degrees):
            adj = construct_graph(degrees)
            if is_connected(adj):
                randomize_graph(adj, num_swaps=50)
                if is_connected(adj):
                    return adj

def find_euler_cycle(adj_input):
    adj = copy.deepcopy(adj_input)
    if not adj:
        return []

    if any(len(neighbors) % 2 != 0 for neighbors in adj.values()):
        raise ValueError("Cykl Eulera wymaga parzystego stopnia każdego wierzchołka.")

    active_nodes = [node for node in adj if adj[node]]
    if not active_nodes:
        return [min(adj)]
    if not is_connected(adj):
        raise ValueError("Graf musi być spójny, aby wyznaczyć cykl Eulera.")

    stack = [active_nodes[0]]
    cycle = []
    while stack:
        current = stack[-1]
        if adj[current]:
            neighbor = adj[current].pop()
            adj[neighbor].remove(current)
            stack.append(neighbor)
        else:
            cycle.append(stack.pop())

    cycle.reverse()
    return cycle

def generate_k_regular_graph(n, k):
    if n <= k or (n * k) % 2 != 0:
        raise ValueError("Niepoprawne parametry dla grafu k-regularnego (warunek n > k oraz n*k parzyste).")
    degrees = [k] * n
    adj = construct_graph(degrees)
    randomize_graph(adj, num_swaps=50)
    return adj

def find_hamiltonian_cycle(adj):
    if not adj:
        return None

    n = len(adj)
    start_node = min(adj)
    path = [start_node]
    visited = {start_node}
    
    def dfs(curr):
        if len(path) == n:
            if start_node in adj[curr]:
                return True
            return False
        for neighbor in sorted(adj[curr]):
            if neighbor not in visited:
                visited.add(neighbor)
                path.append(neighbor)
                if dfs(neighbor):
                    return True
                path.pop()
                visited.remove(neighbor)
        return False

    if dfs(start_node):
        return path + [start_node]
    return None

def read_sequence_from_file(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Nie znaleziono pliku: {filepath}. Utwórz go przed uruchomieniem.")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    return [int(x) for x in content.replace(',', ' ').split()]

if __name__ == "__main__":
    while True:
        print("  ZESTAW 2 - WYBIERZ ZADANIE DO URUCHOMIENIA")
        print("1. Ciąg graficzny")
        print("2. Randomizacja krawędzi z pliku")
        print("3. Spójne składowe z pliku")
        print("4. Losowy graf eulerowski i cykl Eulera")
        print("5. Losowy graf k-regularny")
        print("6. Sprawdzenie cyklu Hamiltona")
        print("0. Wyjście z programu")
        
        choice = input("Wybierz numer zadania: ").strip()
        
        if choice == '0':
            print("Koniec pracy programu.")
            break
            
        elif choice == '1':
            try:
                print("\nZADANIE 1")
                seq = read_sequence_from_file("zad1_wejscie.txt")
                print(f"Wczytany ciąg: {seq}")
                if degree_seq(seq):
                    print("Ciąg JEST graficzny.")
                    g = construct_graph(seq)
                    draw_graph(g, title="Zadanie 1: Konstrukcja grafu z ciągu")
                else:
                    print("Ciąg NIE jest graficzny.")
            except Exception as e:
                print(f"Błąd: {e}")
            quit()
                
        elif choice == '2':
            try:
                print("\nZADANIE 2")
                data = read_sequence_from_file("zad2_wejscie.txt")
                num_swaps = data[0]
                seq = data[1:]
                print(f"Liczba randomizacji: {num_swaps}, Ciąg początkowy: {seq}")
                if degree_seq(seq):
                    g = construct_graph(seq)
                    randomize_graph(g, num_swaps=num_swaps)
                    print("Zrandomizowano pomyślnie.")
                    draw_graph(g, title=f"Zadanie 2: Po {num_swaps} randomizacjach")
                else:
                    print("Początkowy ciąg nie jest graficzny.")
            except Exception as e:
                print(f"Błąd: {e}")
            quit()
                
        elif choice == '3':
            try:
                print("\n--- ZADANIE 3 ---")
                seq = read_sequence_from_file("zad3_wejscie.txt")
                if degree_seq(seq):
                    g = construct_graph(seq)
                    comps = get_components(g)
                    color_map_dict = {}
                    max_size, max_comp_idx = 0, 0
                    
                    for idx, comp in enumerate(comps):
                        col = colorsys.hsv_to_rgb(idx / max(len(comps), 1), 0.65, 0.95)
                        for v in comp:
                            color_map_dict[v] = col
                        print(f"{idx + 1}) " + " ".join(map(str, comp)))
                        if len(comp) > max_size:
                            max_size = len(comp)
                            max_comp_idx = idx + 1
                    print(f"Największa składowa ma numer {max_comp_idx}.")
                    print(f"Największa składowa ma numer {max_comp_idx}.")
                    
                    node_colors = [color_map_dict[v] for v in sorted(g.keys())]
                    
                    draw_graph(g, title="Zadanie 3: Spójne składowe", node_colors=node_colors)
                else:
                    print("Ciąg w pliku zad3_wejscie.txt nie jest graficzny.")
            except Exception as e:
                print(f"Błąd: {e}")
            quit()

        elif choice == '4':
            try:
                print("\n--- ZADANIE 4 ---")
                n = int(input("Podaj liczbę wierzchołków n: ").strip())
                print(f"Generowanie grafu eulerowskiego dla n={n}...")
                g = generate_random_eulerian_graph(n)
                cycle = find_euler_cycle(g)
                print("Cykl Eulera:", "[" + "-".join(map(str, cycle)) + "]")
                draw_graph(g, title=f"Zadanie 4: Graf eulerowski (n={n})")
            except Exception as e:
                print(f"Błąd: {e}")
            quit()    

        elif choice == '5':
            try:
                print("\nZADANIE 5")
                n = int(input("Podaj liczbę wierzchołków n: ").strip())
                k = int(input("Podaj stopień wierzchołków k: ").strip())
                g = generate_k_regular_graph(n, k)
                print(f"Wygenerowano graf {k}-regularny dla n={n}.")
                draw_graph(g, title=f"Zadanie 5: Graf {k}-regularny (n={n}, k={k})")
            except Exception as e:
                print(f"Błąd: {e}")
            quit()

        elif choice == '6':
            try:
                print("\nZADANIE 6")
                print("Wybierz źródło grafu do sprawdzenia cyklu Hamiltona:")
                print("1. Użyj grafu z pliku (zad1_wejscie.txt)")
                print("2. Wygeneruj losowy graf k-regularny (podając n i k)")
                sub_choice = input("Wybór (1 lub 2): ").strip()
                
                g = None
                if sub_choice == '1':
                    seq = read_sequence_from_file("zad1_wejscie.txt")
                    if degree_seq(seq):
                        g = construct_graph(seq)
                elif sub_choice == '2':
                    n = int(input("Podaj n: ").strip())
                    k = int(input("Podaj k: ").strip())
                    g = generate_k_regular_graph(n, k)
                
                if g:
                    ham_cycle = find_hamiltonian_cycle(g)
                    if ham_cycle:
                        print("Graf jest hamiltonowski! Cykl Hamiltona:", "[" + "-".join(map(str, ham_cycle)) + "]")
                    else:
                        print("Graf nie jest hamiltonowski (lub nie znaleziono cyklu).")
                    draw_graph(g, title="Zadanie 6: Sprawdzenie cyklu Hamiltona")
                else:
                    print("Nie udało się utworzyć/wczytać grafu.")
            except Exception as e:
                print(f"Błąd: {e}")
            quit()

        else:
            print("Nieznana opcja. Wybierz liczbę od 0 do 6.")