import numpy as np


#============================ SUDOKU SOLVER =================================#
class SudokuSolver:
    def __init__(self, grid):
        self.grid = np.array(grid)
        self.size = 9
        self.subgrid_size = 3

    def find_empty_cell(self):
        for row in range(self.size):
            for col in range(self.size):
                if self.grid[row, col] == 0:
                    return row, col
        return None

    def is_valid(self, num, row, col):
        if num in self.grid[row, :] or num in self.grid[:, col]:
            return False
        start_row, start_col = row - row % self.subgrid_size, col - col % self.subgrid_size
        if num in self.grid[start_row:start_row + self.subgrid_size, start_col:start_col + self.subgrid_size]:
            return False
        return True

    def get_candidates(self, row, col):
        return [num for num in range(1, self.size + 1) if self.is_valid(num, row, col)]

    def single_candidate(self):
        
        changed = False
        for row in range(self.size):
            for col in range(self.size):
                if self.grid[row, col] == 0:
                    candidates = self.get_candidates(row, col)
                    if len(candidates) == 1:
                        self.grid[row, col] = candidates[0]
                        changed = True
        return changed

    def hidden_single(self):
        changed = False
        for num in range(1, self.size + 1):
            for i in range(self.size):
                row_positions = [(i, j) for j in range(self.size) if self.grid[i, j] == 0 and self.is_valid(num, i, j)]
                if len(row_positions) == 1:
                    self.grid[row_positions[0]] = num
                    changed = True
                col_positions = [(j, i) for j in range(self.size) if self.grid[j, i] == 0 and self.is_valid(num, j, i)]
                if len(col_positions) == 1:
                    self.grid[col_positions[0]] = num
                    changed = True
        return changed

    def naked_pairs(self):
        changed = False
        for unit in self.get_units():
            pairs = {}
            for cell in unit:
                row, col = cell
                if self.grid[row, col] == 0:
                    candidates = tuple(self.get_candidates(row, col))
                    if len(candidates) == 2:
                        pairs.setdefault(candidates, []).append(cell)
            for pair, cells in pairs.items():
                if len(cells) == 2:
                    for cell in unit:
                        if cell not in cells:
                            row, col = cell
                            if self.grid[row, col] == 0:
                                for num in pair:
                                    if num in self.get_candidates(row, col):
                                        self.grid[row, col] = num
                                        changed = True
        return changed
    
    def get_units(self):
        units = []
        for i in range(self.size):
            units.append([(i, j) for j in range(self.size)])  
            units.append([(j, i) for j in range(self.size)])  
        for r in range(0, self.size, self.subgrid_size):
            for c in range(0, self.size, self.subgrid_size):
                units.append([(r + i, c + j) for i in range(self.subgrid_size) for j in range(self.subgrid_size)])
        return units

    def solve(self):
        self.display()
        while True:
            if not (self.single_candidate() or self.hidden_single() or self.naked_pairs()):
                break  
            if self.is_solved():
                self.display()
                return True
        if not self.is_solved():
            self.backtrack_solve()
            self.display()
        return self.is_solved()

    def is_solved(self):
        return all(self.grid[row, col] != 0 for row in range(self.size) for col in range(self.size))

    def backtrack_solve(self):
        empty_cell = self.find_empty_cell()
        if not empty_cell:
            return True
        row, col = empty_cell
        for num in self.get_candidates(row, col):
            self.grid[row, col] = num
            if self.backtrack_solve():
                return True
            self.grid[row, col] = 0
        return False
  
    def get_solving_steps(self):
      steps = []
      
      def backtrack_solve_with_steps(self):
          empty_cell = self.find_empty_cell()
          if not empty_cell:
              return True
          
          row, col = empty_cell
          for num in self.get_candidates(row, col):
              self.grid[row, col] = num
              steps.append((row, col, num))
              
              if backtrack_solve_with_steps(self):
                  return True
                  
              self.grid[row, col] = 0
              steps.append((row, col, 0))  
          return False
      
     
      while True:
          initial_grid = self.grid.copy()
          if self.single_candidate():
              for i in range(self.size):
                  for j in range(self.size):
                      if self.grid[i, j] != initial_grid[i, j]:
                          steps.append((i, j, self.grid[i, j]))
              continue
              
          if self.hidden_single():
              for i in range(self.size):
                  for j in range(self.size):
                      if self.grid[i, j] != initial_grid[i, j]:
                          steps.append((i, j, self.grid[i, j]))
              continue
              
          if self.naked_pairs():
              for i in range(self.size):
                  for j in range(self.size):
                      if self.grid[i, j] != initial_grid[i, j]:
                          steps.append((i, j, self.grid[i, j]))
              continue
              
          break
      
      if not self.is_solved():
          backtrack_solve_with_steps(self)
      
      return steps
    