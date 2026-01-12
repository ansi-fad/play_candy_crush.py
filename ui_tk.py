#!/usr/bin/env python3
# Specifica faptul ca scriptul trebuie rulat cu Python 3

import argparse
# Modul pentru citirea argumentelor din linia de comanda

import tkinter as tk
# Importam biblioteca Tkinter pentru interfata grafica

from tkinter import ttk
# Importam widget-uri moderne din Tkinter (butoane, label-uri etc.)

import random
# Modul pentru generare de valori aleatoare

from play_candycrush import Board, select_non_overlapping
# Importam logica jocului: tabla si functia de selectie a formatiilor


COLOR_MAP = {
    0: '#eeeeee',
    # Culoare pentru celulele goale
    1: '#e74c3c',
    # Culoare pentru bomboana de tip 1
    2: '#f39c12',
    # Culoare pentru bomboana de tip 2
    3: '#2ecc71',
    # Culoare pentru bomboana de tip 3
    4: '#3498db',
    # Culoare pentru bomboana de tip 4
}

CELL_SIZE = 40
# Dimensiunea unei celule (patrat) in pixeli

PADDING = 6
# Spatiul dintre celule


class CandyUI:
    # Clasa care se ocupa de interfata grafica a jocului

    def __init__(self, master, rows=11, cols=11, seed=None, speed=1200):
        # Constructorul clasei

        self.master = master
        # Fereastra principala Tkinter

        self.rows = rows
        # Numarul de randuri ale tablei

        self.cols = cols
        # Numarul de coloane ale tablei

        self.seed = seed
        # Seed pentru random, pentru rezultate deterministe

        self.speed = speed
        # Viteza animatiilor in milisecunde

        self.running = False
        # Flag care indica daca jocul ruleaza sau nu

        # ===== CONTROLS =====
        ctrl = ttk.Frame(master)
        # Cream un container pentru controale

        ctrl.pack(side='top', fill='x', padx=8, pady=8)
        # Pozitionam zona de controale in partea de sus

        self.play_btn = ttk.Button(ctrl, text='Play', command=self.start_game)
        # Buton pentru pornirea jocului

        self.play_btn.pack(side='left')
        # Pozitionam butonul Play

        self.stop_btn = ttk.Button(ctrl, text='Stop', command=self.stop_game)
        # Buton pentru oprirea jocului

        self.stop_btn.pack(side='left', padx=6)
        # Pozitionam butonul Stop

        ttk.Label(ctrl, text='Speed (ms):').pack(side='left', padx=12)
        # Eticheta pentru viteza jocului

        self.speed_var = tk.IntVar(value=self.speed)
        # Variabila legata de valoarea din Spinbox

        ttk.Spinbox(
            ctrl, from_=600, to=4000, increment=200,
            # Limitele si pasul pentru viteza
            textvariable=self.speed_var, width=7,
            # Variabila controlata si latimea
            command=self.update_speed
            # Functie apelata la modificarea valorii
        ).pack(side='left')

        self.status = ttk.Label(ctrl, text='Score: 0 | Swaps: 0')
        # Label pentru afisarea scorului si a mutarilor

        self.status.pack(side='right')
        # Pozitionam statusul in dreapta

        # ===== CANVAS =====
        w = cols * (CELL_SIZE + PADDING) + PADDING
        # Calculam latimea canvas-ului

        h = rows * (CELL_SIZE + PADDING) + PADDING
        # Calculam inaltimea canvas-ului

        self.canvas = tk.Canvas(master, width=w, height=h, bg='white')
        # Cream zona unde desenam tabla de joc

        self.canvas.pack(padx=10, pady=10)
        # Pozitionam canvas-ul

        self.rects = {}
        # Dictionar care retine dreptunghiurile desenate pe canvas

        self.rng = random.Random(seed)
        # Generator random cu seed

        self.board = Board(rows, cols)
        # Cream tabla de joc folosind logica din play_candycrush

        self.score, _ = self.board.resolve_all_cascades(self.rng)
        # Eliminam eventualele formatii initiale si calculam scorul

        self.swaps = 0
        # Initializam numarul de mutari

        self.draw_grid()
        # Desenam tabla initiala

        self.update_status()
        # Actualizam textul de status


    # ===== GAME LOGIC =====

    def update_speed(self):
        # Actualizeaza viteza jocului
        self.speed = max(400, int(self.speed_var.get()))
        # Ne asiguram ca viteza nu scade sub 400 ms

    def start_game(self):
        # Porneste jocul automat
        if self.running:
            return
        # Daca jocul ruleaza deja, iesim

        self.running = True
        # Setam jocul ca fiind pornit

        self.play_btn.config(state='disabled')
        # Dezactivam butonul Play

        self.master.after(300, self.game_loop)
        # Pornim bucla principala dupa o mica intarziere

    def stop_game(self):
        # Opreste jocul
        self.running = False
        # Setam flag-ul ca fals

        self.play_btn.config(state='normal')
        # Reactivam butonul Play

    def game_loop(self):
        # Bucla principala a jocului
        if not self.running:
            return
        # Daca jocul este oprit, iesim

        best = self.board.find_best_swap()
        # Cautam cea mai buna mutare posibila

        if best is None:
            self.stop_game()
            # Daca nu mai exista mutari, oprim jocul
            return

        a, b, _, _ = best
        # Extragem cele doua celule care trebuie interschimbate

        self.highlight_swap(a, b)
        # Evidentiem mutarea pe tabla

        self.board.swap(a, b)
        # Aplicam mutarea pe tabla

        self.swaps += 1
        # Incrementam numarul de mutari

        self.update_status()
        # Actualizam statusul

        self.draw_grid()
        # Redesenenam tabla

        self.master.after(self.speed, self.resolve_cascades)
        # Trecem la rezolvarea cascadelor

    def resolve_cascades(self):
        # Rezolva formatiile aparute dupa o mutare
        if not self.running:
            return

        forms = self.board.detect_formations()
        # Detectam toate formatiile existente

        if not forms:
            self.draw_grid()
            # Daca nu mai sunt formatii, redesenam tabla
            self.master.after(self.speed, self.game_loop)
            # Revenim la bucla principala
            return

        selected = select_non_overlapping(forms)
        # Selectam formatiile fara suprapunere

        self.highlight_elimination(selected)
        # Evidentiem celulele care vor fi eliminate

        self.master.after(self.speed, lambda: self.apply_elimination(selected))
        # Aplicam eliminarea dupa un delay

    def apply_elimination(self, selected):
        # Elimina formatiile selectate
        if not self.running:
            return

        self.board.apply_eliminations(selected)
        # Setam celulele eliminate la 0

        self.board.apply_gravity_and_refill(self.rng)
        # Aplicam gravitatia si generam bomboane noi

        self.score += sum(f.score for f in selected)
        # Adaugam scorul obtinut

        self.update_status()
        # Actualizam statusul

        self.draw_grid()
        # Redesenenam tabla

        self.master.after(self.speed, self.resolve_cascades)
        # Verificam daca mai exista cascade


    # ===== UI HELPERS =====

    def highlight_swap(self, a, b):
        # Evidentiaza celulele implicate intr-un swap
        for cell in (a, b):
            rect = self.rects.get(cell)
            if rect:
                self.canvas.itemconfigure(rect, outline='#8e44ad', width=5)

    def highlight_elimination(self, formations):
        # Evidentiaza celulele care vor fi eliminate
        cells = set()
        for f in formations:
            cells |= f.cells

        for (r, c) in cells:
            rect = self.rects.get((r, c))
            if rect:
                self.canvas.itemconfigure(rect, outline='#e74c3c', width=5)

    def draw_grid(self):
        # Deseneaza intreaga tabla de joc
        self.canvas.delete('all')
        # Stergem tot ce este desenat

        self.rects.clear()
        # Golim dictionarul de dreptunghiuri

        for r in range(self.rows):
            for c in range(self.cols):
                val = self.board.cell(r, c)
                # Citim valoarea celulei

                color = COLOR_MAP[val]
                # Alegem culoarea corespunzatoare

                x1 = PADDING + c * (CELL_SIZE + PADDING)
                y1 = PADDING + r * (CELL_SIZE + PADDING)
                # Coordonatele coltului stanga-sus

                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                # Coordonatele coltului dreapta-jos

                rect = self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color,
                    outline='#333333',
                    width=2
                )
                # Desenam patratul pe canvas

                self.rects[(r, c)] = rect
                # Salvam referinta dreptunghiului

        self.master.update_idletasks()
        # Fortam actualizarea interfetei

    def update_status(self):
        # Actualizeaza textul de status
        self.status.config(text=f'Score: {self.score} | Swaps: {self.swaps}')


# ===== MAIN =====

if __name__ == '__main__':
    # Codul de pornire al aplicatiei

    parser = argparse.ArgumentParser()
    # Cream parser pentru argumente

    parser.add_argument('--seed', type=int, default=None)
    # Argument pentru seed random

    parser.add_argument('--speed', type=int, default=1200)
    # Argument pentru viteza jocului

    args = parser.parse_args()
    # Citim argumentele

    root = tk.Tk()
    # Cream fereastra principala

    root.title('Candy Crush – Visual Automator')
    # Setam titlul ferestrei

    CandyUI(
        root,
        rows=11,
        cols=11,
        seed=args.seed,
        speed=args.speed
    )
    # Initializam interfata jocului

    root.mainloop()
    # Pornim bucla grafica Tkinter
