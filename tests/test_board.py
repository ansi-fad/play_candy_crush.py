from collections import deque
# Importăm deque, o coadă eficientă pentru operații FIFO,
# folosită aici pentru parcurgerea BFS (Breadth-First Search)


class Formation:
    def __init__(self, cells, value):
        # Constructorul clasei Formation

        self.cells = set(cells)
        # Salvăm celulele formațiunii ca set pentru:
        # - acces rapid
        # - evitarea duplicatelor

        self.value = value
        # Salvăm tipul de bomboană (valoarea din grid)


class Board:
    def __init__(self, rows, cols, grid):
        # Constructorul tablei de joc

        self.rows = rows
        # Numărul de rânduri ale tablei

        self.cols = cols
        # Numărul de coloane ale tablei

        self.grid = grid
        # Matricea care conține valorile bomboanelor


    def in_bounds(self, r, c):
        # Verifică dacă o poziție este în interiorul tablei

        return 0 <= r < self.rows and 0 <= c < self.cols
        # True dacă r și c sunt valide, False altfel


    def detect_formations(self):
        # Funcția principală care detectează toate formațiunile valide

        visited = [[False]*self.cols for _ in range(self.rows)]
        # Matrice care marchează celulele deja vizitate,
        # pentru a nu procesa aceeași celulă de mai multe ori

        formations = []
        # Listă în care vom salva formațiunile detectate

        directions = [(-1,0), (1,0), (0,-1), (0,1)]
        # Direcțiile posibile de deplasare:
        # sus, jos, stânga, dreapta


        for r in range(self.rows):
            # Parcurgem fiecare rând al tablei

            for c in range(self.cols):
                # Parcurgem fiecare coloană

                if visited[r][c]:
                    # Dacă celula a fost deja procesată
                    continue
                    # Sărim peste ea

                value = self.grid[r][c]
                # Luăm valoarea bomboanei din celula curentă

                queue = deque([(r, c)])
                # Inițializăm coada BFS cu poziția curentă

                visited[r][c] = True
                # Marcăm celula ca fiind vizitată

                cells = [(r, c)]
                # Listă care va conține toate celulele conectate
                # cu aceeași valoare


                while queue:
                    # Cât timp mai avem celule de procesat în coadă

                    cr, cc = queue.popleft()
                    # Scoatem prima celulă din coadă

                    for dr, dc in directions:
                        # Verificăm fiecare direcție posibilă

                        nr, nc = cr + dr, cc + dc
                        # Calculăm coordonatele vecinului

                        if (
                            self.in_bounds(nr, nc)
                            # Verificăm dacă vecinul e în tablă
                            and not visited[nr][nc]
                            # Verificăm dacă nu a fost deja vizitat
                            and self.grid[nr][nc] == value
                            # Verificăm dacă are aceeași valoare
                        ):
                            visited[nr][nc] = True
                            # Marcăm vecinul ca vizitat

                            queue.append((nr, nc))
                            # Îl adăugăm în coada BFS

                            cells.append((nr, nc))
                            # Îl adăugăm în lista celulelor conectate


                if len(cells) >= 3:
                    # Verificăm dacă grupul are cel puțin 3 celule

                    if self._is_valid_shape(cells):
                        # Verificăm dacă grupul formează o linie
                        # sau o combinație validă (T / L / +)

                        formations.append(Formation(cells, value))
                        # Dacă da, îl adăugăm la lista de formațiuni


        return formations
        # Returnăm toate formațiunile detectate


    def _is_valid_shape(self, cells):
        # Funcție ajutătoare care verifică dacă forma este validă

        rows = {}
        # Dicționar: cheie = rând, valoare = câte celule sunt pe acel rând

        cols = {}
        # Dicționar: cheie = coloană, valoare = câte celule sunt pe acea coloană


        for r, c in cells:
            # Parcurgem fiecare celulă din formațiune

            rows.setdefault(r, 0)
            # Inițializăm contorul pentru rând dacă nu există

            cols.setdefault(c, 0)
            # Inițializăm contorul pentru coloană dacă nu există

            rows[r] += 1
            # Incrementăm numărul de celule pe rândul r

            cols[c] += 1
            # Incrementăm numărul de celule pe coloana c


        has_row = any(v >= 3 for v in rows.values())
        # True dacă există un rând cu cel puțin 3 celule

        has_col = any(v >= 3 for v in cols.values())
        # True dacă există o coloană cu cel puțin 3 celule

        return has_row or has_col
        # Forma este validă dacă există cel puțin:
        # - o linie orizontală de 3
        # SAU
        # - o linie verticală de 3
