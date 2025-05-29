import tkinter as tk
import random
from tkinter import messagebox
import sys

def generate_board(rows, cols):
    # Generate a board with random mines
    choices = ["E"] * 5 + ["M"]
    board = [[random.choice(choices) for _ in range(cols)] for _ in range(rows)]
    mine_count = sum(cell == "M" for row in board for cell in row)
    return board, mine_count

def number_board(board):
    # Create a board with numbers indicating adjacent mines
    rows, cols = len(board), len(board[0])
    numbered = [["0"] * cols for _ in range(rows)]
    for i in range(rows):
        for j in range(cols):
            if board[i][j] == "M":
                numbered[i][j] = "M"
            else:
                count = 0
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        ni, nj = i + dr, j + dc
                        if 0 <= ni < rows and 0 <= nj < cols and board[ni][nj] == "M":
                            count += 1
                numbered[i][j] = str(count)
    return numbered

class Minesweeper:
    def __init__(self, rows, cols):
        self.rows, self.cols = rows, cols
        self.solution, self.mine_count = generate_board(rows, cols)
        self.numbers = number_board(self.solution)
        self.revealed = [[False]*cols for _ in range(rows)]
        self.flags = set()
        self.remaining = rows * cols - self.mine_count

    def reveal(self, i, j):
        if self.revealed[i][j] or (i, j) in self.flags:
            return set()
        to_reveal = set()
        self._dfs(i, j, to_reveal)
        return to_reveal

    def _dfs(self, i, j, to_reveal):
        if not (0 <= i < self.rows and 0 <= j < self.cols):
            return
        if self.revealed[i][j] or (i, j) in self.flags:
            return
        self.revealed[i][j] = True
        to_reveal.add((i, j))
        if self.numbers[i][j] == "0":
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr or dc:
                        self._dfs(i + dr, j + dc, to_reveal)

    def is_mine(self, i, j):
        return self.solution[i][j] == "M"

    def is_win(self):
        return sum(sum(row) for row in self.revealed) == self.remaining

class MinesweeperUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Minesweeper")
        self.setup_menu()
        self.root.mainloop()

    def setup_menu(self):
        self.clear()
        tk.Label(self.root, text="Select Difficulty").pack(pady=10)
        for text, dims in [("Easy", (6, 15)), ("Medium", (10, 25)), ("Hard", (14, 35))]:
            tk.Button(self.root, text=text, width=10,
                      command=lambda d=dims: self.start_game(*d)).pack(pady=5)
        self.root.protocol("WM_DELETE_WINDOW", self.root.quit)

    def start_game(self, rows, cols):
        self.game = Minesweeper(rows, cols)
        self.buttons = {}
        self.clear()
        frame = tk.Frame(self.root)
        frame.pack()
        for i in range(rows):
            for j in range(cols):
                btn = tk.Button(frame, text=" ", width=3, height=1,
                                command=lambda i=i, j=j: self.on_left(i, j))
                btn.bind("<Button-3>", lambda e, i=i, j=j: self.on_right(i, j))
                btn.grid(row=i, column=j)
                self.buttons[(i, j)] = btn
        tk.Button(self.root, text="New Game", command=self.setup_menu).pack(pady=5)

    def on_left(self, i, j):
        if (i, j) in self.game.flags or self.game.revealed[i][j]:
            return
        if self.game.is_mine(i, j):
            self.reveal_all_mines()
            self.end_game(False)
            return
        to_reveal = self.game.reveal(i, j)
        for x, y in to_reveal:
            val = self.game.numbers[x][y]
            self.buttons[(x, y)].config(text="" if val == "0" else val, state="disabled", relief=tk.SUNKEN)
        if self.check_win():
            self.end_game(True)

    def on_right(self, i, j):
        btn = self.buttons[(i, j)]
        if self.game.revealed[i][j]:
            return
        if (i, j) in self.game.flags:
            self.game.flags.remove((i, j))
            btn.config(text=" ")
        else:
            self.game.flags.add((i, j))
            btn.config(text="F")

    def reveal_all_mines(self):
        for (i, j), btn in self.buttons.items():
            if self.game.is_mine(i, j):
                btn.config(text="M", fg="red")

    def check_win(self):
        # Win if all non-mine cells are revealed
        count = sum(self.game.revealed[i][j] for i in range(self.game.rows) for j in range(self.game.cols) if not self.game.is_mine(i, j))
        return count == self.game.remaining

    def end_game(self, won):
        msg = "You Win!" if won else "Game Over"
        again = messagebox.askyesno(msg, f"{msg}\nPlay again?")
        if again:
            self.setup_menu()
        else:
            self.root.quit()

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    MinesweeperUI()