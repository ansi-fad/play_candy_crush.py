#!/usr/bin/env python3
# Shebang: spune sistemului ca fisierul se ruleaza cu Python 3

import argparse
# Modul pentru a citi argumente din linia de comanda (ex: --games 100)

import csv
# Modul pentru a scrie rezultate in fisiere CSV

import os
# Modul pentru lucrul cu fisiere si directoare

import random
# Modul pentru generare de numere aleatoare (bomboane, refill)

import sys
# Modul pentru interactiune cu sistemul (nu este folosit direct aici)

from collections import defaultdict, namedtuple
# namedtuple este folosit pentru structura Formation

from copy import deepcopy
# deepcopy permite copierea completa a grid-ului fara referinte comune


# Definitie pentru o formatie gasita pe tabla
# cells = set de coordonate
# score = punctajul formatiei
# type = tipul formatiei (LINE3, L33 etc.)
Formation = namedtuple('Formation', ['cells', 'score', 'type'])


# Dictionar cu punctajele pentru fiecare tip de formatie
SCORES = {
    'LINE3': 5,    # linie de 3
    'LINE4': 10,   # linie de 4
    'LINE5': 50,   # linie de 5 sau mai mare
    'L33': 20,     # forma de L
    'T333': 30,    # forma de T
}


class Board:
    # Clasa care reprezinta tabla de joc

    def __init__(self, rows=11, cols=11, seed=None, grid=None):
        # Constructorul clasei Board

        self.rows = rows
        # Numar de randuri

        self.cols = cols
        # Numar de coloane

        if grid is not None:
            # Daca primim un grid deja existent
            self.grid = [list(r) for r in grid]
            # Copiem fiecare rand ca lista separata
        else:
            # Altfel generam un grid random
            self.grid = [[random.randint(1, 4) for _ in range(cols)] for _ in range(rows)]
            # Fiecare celula primeste o bomboana intre 1 si 4

        self.rng = random.Random(seed)
        # Generator random local pentru reproductibilitate


    def copy(self):
        # Creeaza o copie completa a tablei
        return Board(self.rows, self.cols, grid=deepcopy(self.grid))


    def in_bounds(self, r, c):
        # Verifica daca o coordonata este in interiorul tablei
        return 0 <= r < self.rows and 0 <= c < self.cols


    def cell(self, r, c):
        # Returneaza valoarea dintr-o celula
        return self.grid[r][c]


    def set_cell(self, r, c, v):
        # Seteaza o valoare intr-o celula
        self.grid[r][c] = v


    def swap(self, a, b):
        # Face swap intre doua celule a si b
        (r1, c1), (r2, c2) = a, b
        # Despachetam coordonatele

        self.grid[r1][c1], self.grid[r2][c2] = self.grid[r2][c2], self.grid[r1][c1]
        # Schimbam valorile dintre ele


    def detect_formations(self):
        # Detecteaza toate formatiile existente pe tabla
        # Returneaza o lista de obiecte Formation (pot fi suprapuse)

        forms = []
        # Lista in care salvam toate formatiile gasite

        # ================= LINII ORIZONTALE =================
        for r in range(self.rows):
            c = 0
            # Incepem de la prima coloana

            while c < self.cols:
                val = self.grid[r][c]
                # Valoarea curenta

                if val == 0:
                    # Daca celula este goala, sarim peste
                    c += 1
                    continue

                start = c
                # Memorăm inceputul secventei

                while c + 1 < self.cols and self.grid[r][c + 1] == val:
                    # Avansam cat timp bomboanele sunt identice
                    c += 1

                length = c - start + 1
                # Lungimea secventei gasite

                if length >= 3:
                    # Daca avem minim 3 la rand
                    if length == 3:
                        cells = {(r, cc) for cc in range(start, start + 3)}
                        forms.append(Formation(cells, SCORES['LINE3'], 'LINE3'))
                    elif length == 4:
                        cells = {(r, cc) for cc in range(start, start + 4)}
                        forms.append(Formation(cells, SCORES['LINE4'], 'LINE4'))
                    else:
                        cells = {(r, cc) for cc in range(start, start + length)}
                        forms.append(Formation(cells, SCORES['LINE5'], 'LINE5'))

                c += 1
                # Continuam cautarea dupa secventa


        # ================= LINII VERTICALE =================
        for c in range(self.cols):
            r = 0
            # Pornim de sus in jos

            while r < self.rows:
                val = self.grid[r][c]

                if val == 0:
                    r += 1
                    continue

                start = r

                while r + 1 < self.rows and self.grid[r + 1][c] == val:
                    r += 1

                length = r - start + 1

                if length >= 3:
                    if length == 3:
                        cells = {(rr, c) for rr in range(start, start + 3)}
                        forms.append(Formation(cells, SCORES['LINE3'], 'LINE3'))
                    elif length == 4:
                        cells = {(rr, c) for rr in range(start, start + 4)}
                        forms.append(Formation(cells, SCORES['LINE4'], 'LINE4'))
                    else:
                        cells = {(rr, c) for rr in range(start, start + length)}
                        forms.append(Formation(cells, SCORES['LINE5'], 'LINE5'))

                r += 1


        # ================= FORME DE L =================
        for r in range(self.rows):
            for c in range(self.cols):
                v = self.grid[r][c]

                if v == 0:
                    continue

                # L spre dreapta jos
                if self._match_cells_color([(r, c + i) for i in range(3)] + [(r + i, c) for i in range(3)], v):
                    cells = {(r, c + i) for i in range(3)} | {(r + i, c) for i in range(3)}
                    forms.append(Formation(cells, SCORES['L33'], 'L33'))

                # L spre stanga jos
                if self._match_cells_color([(r, c - i) for i in range(3)] + [(r + i, c) for i in range(3)], v):
                    cells = {(r, c - i) for i in range(3)} | {(r + i, c) for i in range(3)}
                    forms.append(Formation(cells, SCORES['L33'], 'L33'))

                # L spre dreapta sus
                if self._match_cells_color([(r, c + i) for i in range(3)] + [(r - i, c) for i in range(3)], v):
                    cells = {(r, c + i) for i in range(3)} | {(r - i, c) for i in range(3)}
                    forms.append(Formation(cells, SCORES['L33'], 'L33'))

                # L spre stanga sus
                if self._match_cells_color([(r, c - i) for i in range(3)] + [(r - i, c) for i in range(3)], v):
                    cells = {(r, c - i) for i in range(3)} | {(r - i, c) for i in range(3)}
                    forms.append(Formation(cells, SCORES['L33'], 'L33'))


        # ================= FORME DE T =================
        for r in range(self.rows):
            for c in range(self.cols):
                v = self.grid[r][c]

                if v == 0:
                    continue

                # T cu tija in jos
                if self.in_bounds(r + 2, c) and self.in_bounds(r + 1, c - 1) and self.in_bounds(r + 1, c + 1):
                    coords = [(r + i, c) for i in range(3)] + [(r + 1, c - 1), (r + 1, c + 1)]
                    if self._match_cells_color(coords, v):
                        forms.append(Formation(set(coords), SCORES['T333'], 'T333'))

                # T cu tija in sus
                if self.in_bounds(r - 2, c) and self.in_bounds(r - 1, c - 1) and self.in_bounds(r - 1, c + 1):
                    coords = [(r - i, c) for i in range(3)] + [(r - 1, c - 1), (r - 1, c + 1)]
                    if self._match_cells_color(coords, v):
                        forms.append(Formation(set(coords), SCORES['T333'], 'T333'))

                # T orizontal spre dreapta
                if self.in_bounds(r, c + 2) and self.in_bounds(r - 1, c + 1) and self.in_bounds(r + 1, c + 1):
                    coords = [(r, c + i) for i in range(3)] + [(r - 1, c + 1), (r + 1, c + 1)]
                    if self._match_cells_color(coords, v):
                        forms.append(Formation(set(coords), SCORES['T333'], 'T333'))

                # T orizontal spre stanga
                if self.in_bounds(r, c - 2) and self.in_bounds(r - 1, c - 1) and self.in_bounds(r + 1, c - 1):
                    coords = [(r, c - i) for i in range(3)] + [(r - 1, c - 1), (r + 1, c - 1)]
                    if self._match_cells_color(coords, v):
                        forms.append(Formation(set(coords), SCORES['T333'], 'T333'))

        return forms
    def _match_cells_color(self, coords, color):
        # Verifica daca toate coordonatele din lista au aceeasi culoare

        for (r, c) in coords:
            # Parcurgem fiecare coordonata

            if not self.in_bounds(r, c):
                # Daca macar una este in afara tablei
                return False

            if self.grid[r][c] != color:
                # Daca culoarea nu este cea cautata
                return False

        return True
        # Daca toate verificarile au trecut


    def apply_eliminations(self, formations):
        """
        Primeste o lista de formatii deja selectate (fara suprapuneri).
        Seteaza celulele respective la 0 (eliminare).
        Returneaza numarul total de celule eliminate.
        """

        removed = 0
        # Contor pentru cate celule au fost eliminate

        for f in formations:
            # Parcurgem fiecare formatie

            for (r, c) in f.cells:
                # Parcurgem fiecare celula din formatie

                if self.grid[r][c] != 0:
                    # Daca nu a fost deja eliminata
                    self.grid[r][c] = 0
                    # Eliminam celula
                    removed += 1
                    # Incrementam contorul

        return removed
        # Returnam totalul


    def apply_gravity_and_refill(self, rng=None):
        # Aplica gravitatia si reumple tabla cu bomboane noi

        if rng is None:
            rng = random
            # Daca nu primim RNG, folosim random global

        for c in range(self.cols):
            # Procesam fiecare coloana separat

            write_r = self.rows - 1
            # Pozitia unde va cadea urmatoarea bomboana

            for r in range(self.rows - 1, -1, -1):
                # Parcurgem coloana de jos in sus

                if self.grid[r][c] != 0:
                    # Daca gasim o bomboana
                    self.grid[write_r][c] = self.grid[r][c]
                    # O mutam in jos
                    write_r -= 1
                    # Mutam pozitia de scriere in sus

            for r in range(write_r, -1, -1):
                # Umplem restul coloanei cu bomboane noi
                self.grid[r][c] = rng.randint(1, 4)
                # Generam bomboane random


    def resolve_all_cascades(self, rng=None):
        """
        Repeta:
        - detectare formatii
        - selectare fara suprapuneri
        - eliminare
        - gravitatie + refill
        pana cand tabla este stabila.
        Returneaza scorul total si numarul de cascade.
        """

        total_score = 0
        # Scor acumulat

        total_cascades = 0
        # Numar total de cascade

        while True:
            forms = self.detect_formations()
            # Detectam toate formatiile existente

            if not forms:
                # Daca nu mai exista formatii
                break

            selected = select_non_overlapping(forms)
            # Alegem doar formatiile fara suprapuneri

            if not selected:
                # Daca nu se poate selecta nimic
                break

            for f in selected:
                # Adunam scorul fiecarei formatii
                total_score += f.score

            self.apply_eliminations(selected)
            # Eliminam formatiile

            self.apply_gravity_and_refill(rng=rng)
            # Aplicam gravitatia si refill

            total_cascades += 1
            # Incrementam numarul de cascade

        return total_score, total_cascades
        # Returnam scorul si cascadele


    def any_possible_swap_creates_formation(self):
        """
        Verifica daca exista macar un swap valid
        care produce o formatie.
        """

        for r in range(self.rows):
            for c in range(self.cols):
                for dr, dc in ((1, 0), (0, 1)):
                    # Verificam doar dreapta si jos

                    r2, c2 = r + dr, c + dc

                    if not self.in_bounds(r2, c2):
                        continue

                    b = self.copy()
                    # Lucram pe o copie

                    b.swap((r, c), (r2, c2))
                    # Aplicam swap

                    if b.detect_formations():
                        # Daca apare o formatie
                        return True

        return False
        # Nu exista mutari valide


    def find_best_swap(self):
        """
        Cauta cel mai bun swap posibil:
        - simuleaza fiecare swap
        - rezolva cascadele
        - alege swap-ul cu scor maxim
        """

        best = None
        # Variabila pentru cel mai bun swap

        for r in range(self.rows):
            for c in range(self.cols):
                for dr, dc in ((1, 0), (0, 1)):

                    r2, c2 = r + dr, c + dc

                    if not self.in_bounds(r2, c2):
                        continue

                    b = self.copy()
                    # Copiem tabla

                    b.swap((r, c), (r2, c2))
                    # Aplicam swap

                    gained, casc = b.resolve_all_cascades()
                    # Simulam cascadele

                    if gained > 0:
                        # Daca mutarea produce puncte
                        key = (gained, -casc, -r, -c, -r2, -c2)
                        # Criteriu de comparare

                        if best is None or key > best[0]:
                            best = (key, (r, c), (r2, c2), gained, casc)

        if best is None:
            return None

        return best[1], best[2], best[3], best[4]


def select_non_overlapping(forms):
    """
    Selecteaza greedy formatiile:
    - sortate descrescator dupa scor
    - fara suprapuneri de celule
    """

    forms_sorted = sorted(forms, key=lambda f: (-f.score, -len(f.cells)))
    # Sortam dupa scor si marime

    chosen = []
    # Lista de formatii alese

    used = set()
    # Celule deja folosite

    for f in forms_sorted:
        if f.cells & used:
            continue
        chosen.append(f)
        used |= f.cells

    return chosen


def play_single_game(rows=11, cols=11, target=10000, seed=None, rng=None):
    # Ruleaza un singur joc complet

    if rng is None:
        rng = random.Random(seed)

    board = Board(rows, cols, seed=None)
    # Initializam tabla

    refill_rng = random.Random(seed)
    # RNG separat pentru refill

    initial_score, initial_casc = board.resolve_all_cascades(rng=refill_rng)
    # Eliminam formatiile initiale

    total_score = initial_score
    total_swaps = 0
    total_cascades = initial_casc
    moves_to_10000 = None

    while True:
        if total_score >= target and moves_to_10000 is None:
            moves_to_10000 = total_swaps

        best = board.find_best_swap()
        # Cautam cea mai buna mutare

        if best is None:
            # Daca nu mai exista mutari
            return {
                'points': total_score,
                'swaps': total_swaps,
                'total_cascades': total_cascades,
                'reached_target': total_score >= target,
                'stopping_reason': 'NO_MOVES',
                'moves_to_10000': moves_to_10000 if total_score >= target else ''
            }

        a, b, gained, casc = best

        board.swap(a, b)
        # Aplicam swap-ul

        total_swaps += 1

        sc, casc_here = board.resolve_all_cascades(rng=refill_rng)
        # Rezolvam cascadele

        total_score += sc
        total_cascades += casc_here

        if total_score >= target:
            return {
                'points': total_score,
                'swaps': total_swaps,
                'total_cascades': total_cascades,
                'reached_target': True,
                'stopping_reason': 'REACHED_TARGET',
                'moves_to_10000': moves_to_10000
            }


def ensure_dir(path):
    # Creeaza directorul daca nu exista

    d = os.path.dirname(path)

    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)


def main():
    # Functia principala

    parser = argparse.ArgumentParser()
    # Parser pentru argumente CLI

    parser.add_argument('--games', type=int, default=100)
    parser.add_argument('--rows', type=int, default=11)
    parser.add_argument('--cols', type=int, default=11)
    parser.add_argument('--target', type=int, default=10000)
    parser.add_argument('--out', type=str, default='results/summary.csv')
    parser.add_argument('--seed', type=int, default=None)

    args = parser.parse_args()

    ensure_dir(args.out)
    random.seed(args.seed)

    records = []

    for gid in range(args.games):
        game_seed = args.seed + gid if args.seed is not None else None
        result = play_single_game(args.rows, args.cols, args.target, seed=game_seed)
        records.append([gid, result['points'], result['swaps'], result['total_cascades'],
                        result['reached_target'], result['stopping_reason'], result['moves_to_10000']])

    with open(args.out, 'w', newline='') as fh:
        writer = csv.writer(fh)
        writer.writerow(['game_id', 'points', 'swaps', 'total_cascades',
                         'reached_target', 'stopping_reason', 'moves_to_10000'])
        writer.writerows(records)


if __name__ == '__main__':
    main()
