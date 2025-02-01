import numpy as np
import random

#=========================== RANDOM BOARD GENERATOR BASED ON DIFFICULTY =================================#

class SudokuBoardGenerator:
    def __init__(self):
        self.size = 9
        self.subgrid_size = 3
        self.board = np.zeros((self.size, self.size), dtype=int)
    
    def generate_full_board(self):
        self.board = np.zeros((self.size, self.size), dtype=int)
        self.fill_board()
    
    def fill_board(self):
        def backtrack_fill(r, c):
            if r == self.size:
                return True
            if c == self.size:
                return backtrack_fill(r + 1, 0)
            numbers = list(range(1, self.size + 1))
            random.shuffle(numbers)
            for num in numbers:
                if self.is_valid(num, r, c):
                    self.board[r, c] = num
                    if backtrack_fill(r, c + 1):
                        return True
                    self.board[r, c] = 0
            return False
        
        backtrack_fill(0, 0)
    
    def is_valid(self, num, row, col):
        if num in self.board[row, :] or num in self.board[:, col]:
            return False
        start_row, start_col = row - row % self.subgrid_size, col - col % self.subgrid_size
        if num in self.board[start_row:start_row + self.subgrid_size, start_col:start_col + self.subgrid_size]:
            return False
        return True
    
    def remove_numbers(self, difficulty):
        if difficulty == "easy":
            cells_to_remove = 30
        elif difficulty == "medium":
            cells_to_remove = 40
        elif difficulty == "hard":
            cells_to_remove = 50
        elif difficulty == "expert":
            cells_to_remove = 60
        else:
            raise ValueError("Invalid difficulty level")
        
        removed = 0
        while removed < cells_to_remove:
            row, col = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
            if self.board[row, col] != 0:
                self.board[row, col] = 0
                removed += 1
    
    def generate(self, difficulty="easy"):
        self.generate_full_board()
        self.remove_numbers(difficulty)
        return self.board