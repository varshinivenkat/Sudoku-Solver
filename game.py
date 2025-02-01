import pygame
import sys
import time
import numpy as np
from pygame import gfxdraw
import random

import constants as c
from button import Button, draw_rounded_rect
from board_generator import SudokuBoardGenerator
from solver import SudokuSolver

#============================ CREATE WINDOWS AND ACTUAL GAME PLAYING =================================#
class SudokuGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((c.WINDOW_WIDTH, c.WINDOW_HEIGHT))
        pygame.display.set_caption("Sudoku")
        self.clock = pygame.time.Clock()
        self.generator = SudokuBoardGenerator()
        self.current_screen = "menu"
        self.selected_cell = None
        self.game_board = None
        self.original_board = None
        self.start_time = None
        self.elapsed_time = 0
        self.initialize_buttons()
        self.font = pygame.font.Font(None, 36)
        self.errors = set()
        self.clashing_cells = set()
        self.solver = None
        self.solving_animation = False
        self.solving_delay = 50
        self.last_solve_step = 0
        
    def initialize_buttons(self):
        self.menu_buttons = []
        difficulties = ["Easy", "Medium", "Hard", "Expert"]
        start_y = 200
        for i, diff in enumerate(difficulties):
            x = (c.WINDOW_WIDTH - c.BUTTON_WIDTH) // 2
            y = start_y + i * (c.BUTTON_HEIGHT + c.BUTTON_MARGIN)
            self.menu_buttons.append(Button(x, y, c.BUTTON_WIDTH, c.BUTTON_HEIGHT, diff))
            
        self.back_button = Button(20, 20, 100, 40, "Back")
        self.solve_button = Button(c.WINDOW_WIDTH - 240, 20, 100, 40, "Solve")
        self.reset_button = Button(c.WINDOW_WIDTH - 120, 20, 100, 40, "Reset")
        
    def start_game(self, difficulty):
      self.game_board = self.generator.generate(difficulty.lower())
      self.original_board = np.copy(self.game_board) 
      self.current_screen = "game"
      self.start_time = time.time()
        
    def draw_menu(self):
        self.screen.fill(c.PASTEL_BLUE)
        title_font = pygame.font.Font(None, 72)
        title_text = title_font.render("SUDOKU", True, c.DARK_PASTEL_BLUE)
        title_rect = title_text.get_rect(center=(c.WINDOW_WIDTH//2, 100))
        self.screen.blit(title_text, title_rect)
        
        for button in self.menu_buttons:
            button.draw(self.screen)

    def is_board_complete(self):
      if len(self.errors) > 0:  
          return False
          
      for i in range(c.c.GRID_SIZE):
          for j in range(c.c.GRID_SIZE):
              if self.game_board[i][j] == 0:
                  return False
      return True

    def draw_congratulations(self):
        modal_x = (c.WINDOW_WIDTH - c.MODAL_WIDTH) // 2
        modal_y = (c.WINDOW_HEIGHT - c.MODAL_HEIGHT) // 2
        modal_rect = pygame.Rect(modal_x, modal_y, c.MODAL_WIDTH, c.MODAL_HEIGHT)
        
        s = pygame.Surface((c.WINDOW_WIDTH, c.WINDOW_HEIGHT))
        s.fill((0, 0, 0))
        s.set_alpha(128)
        self.screen.blit(s, (0, 0))
        
        draw_rounded_rect(self.screen, c.PASTEL_BLUE, modal_rect, 20)
        pygame.draw.rect(self.screen, c.DARK_PASTEL_BLUE, modal_rect, 3, border_radius=20)
       
        title_font = pygame.font.Font(None, 48)
        text_font = pygame.font.Font(None, 36)
        
        title = title_font.render("Congratulations!", True, c.DARK_PASTEL_BLUE)
        title_rect = title.get_rect(centerx= c.WINDOW_WIDTH//2, top=modal_y + 30)
        self.screen.blit(title, title_rect)
        
        minutes = int(self.elapsed_time // 60)
        seconds = int(self.elapsed_time % 60)
        time_text = f"Time: {minutes:02d}:{seconds:02d}"
        time_surface = text_font.render(time_text, True, c.BLACK)
        time_rect = time_surface.get_rect(centerx= c.WINDOW_WIDTH//2, top=modal_y + 100)
        self.screen.blit(time_surface, time_rect)
        
        continue_button = Button(
            (c.WINDOW_WIDTH - c.CONGRATS_BUTTON_WIDTH) // 2,
            modal_y + c.MODAL_HEIGHT - 80,
            c.CONGRATS_BUTTON_WIDTH,
            c.CONGRATS_BUTTON_HEIGHT,
            "Continue"
        )
        continue_button.draw(self.screen)
        return continue_button
            
    def validate_cell(self, row, col, value):
      if value == 0:
          self.errors.discard((row, col))
          self.clashing_cells.clear()
          return True
          
      clashing = set()
      is_valid = True
      
      # Check row
      for j in range(c.c.GRID_SIZE):
          if j != col and self.game_board[row][j] == value:
              clashing.add((row, j))
              is_valid = False
              
      # Check column
      for i in range(c.c.GRID_SIZE):
          if i != row and self.game_board[i][col] == value:
              clashing.add((i, col))
              is_valid = False
              
      # Check 3x3 box
      box_row, box_col = 3 * (row // 3), 3 * (col // 3)
      for i in range(box_row, box_row + 3):
          for j in range(box_col, box_col + 3):
              if (i != row or j != col) and self.game_board[i][j] == value:
                  clashing.add((i, j))
                  is_valid = False
      
      # Update error and clashing cells sets
      if not is_valid:
          self.errors.add((row, col))
          self.clashing_cells = clashing
      else:
          self.errors.discard((row, col))
          self.clashing_cells.clear()
          
      return is_valid

    def handle_key_input(self, key):
      if self.selected_cell:
          row, col = self.selected_cell
          if self.original_board[row][col] != 0: 
              return
              
          if key in range(pygame.K_1, pygame.K_9 + 1):
              num = key - pygame.K_0
              self.game_board[row][col] = num
              self.validate_cell(row, col, num)
              
              if self.is_board_complete():
                  self.current_screen = "congratulations"
                  self.elapsed_time = time.time() - self.start_time
                  self.start_time = None 
                  
          elif key == pygame.K_BACKSPACE or key == pygame.K_0:
              self.game_board[row][col] = 0
              self.validate_cell(row, col, 0)

    def draw_grid(self):
        grid_width = c.GRID_SIZE * c.CELL_SIZE
        grid_height = c.GRID_SIZE * c.CELL_SIZE
        start_x = (c.WINDOW_WIDTH - grid_width) // 2
        start_y = (c.WINDOW_HEIGHT - grid_height) // 2
        for i in range(c.GRID_SIZE):
            for j in range(c.GRID_SIZE):
                x = start_x + j * c.CELL_SIZE
                y = start_y + i * c.CELL_SIZE
                cell_rect = pygame.Rect(x, y, c.CELL_SIZE, c.CELL_SIZE)
               
                if (i, j) in self.errors:
                    pygame.draw.rect(self.screen, c.RED, cell_rect)
                elif (i, j) in self.clashing_cells:
                    pygame.draw.rect(self.screen, c.LIGHT_RED, cell_rect)
                elif self.selected_cell == (i, j):
                    pygame.draw.rect(self.screen, c.DARK_PASTEL_BLUE, cell_rect)
                else:
                    pygame.draw.rect(self.screen, c.WHITE, cell_rect)
                
                if self.game_board[i][j] != 0:
                    color = c.BLACK if self.original_board[i][j] != 0 else c.GRAY
                    value = str(self.game_board[i][j])
                    text = self.font.render(value, True, color)
                    text_rect = text.get_rect(center=(x + c.CELL_SIZE//2, y + c.CELL_SIZE//2))
                    self.screen.blit(text, text_rect)
                
                pygame.draw.rect(self.screen, c.BLACK, cell_rect, 1)
        
        for i in range(4):
            thick_line_pos = i * (c.CELL_SIZE * 3)
            pygame.draw.line(self.screen, c.BLACK, 
                          (start_x + thick_line_pos, start_y),
                          (start_x + thick_line_pos, start_y + grid_height), 3)
            pygame.draw.line(self.screen, c.BLACK,
                          (start_x, start_y + thick_line_pos),
                          (start_x + grid_width, start_y + thick_line_pos), 3)
    
    def solve_step(self):
        if not hasattr(self, 'solver_steps'):
            solver = SudokuSolver(self.game_board)
            
            self.valid_entries = np.zeros_like(self.game_board, dtype=bool)
            for i in range(c.GRID_SIZE):
                for j in range(c.GRID_SIZE):
                    if self.game_board[i][j] != 0 and (i, j) not in self.errors:
                        self.valid_entries[i][j] = True
            
            self.user_entries = np.where(self.valid_entries, self.game_board, 0)
            self.solver_steps = solver.get_solving_steps()
            self.current_step = 0
            return
        
        current_time = pygame.time.get_ticks()
        if current_time - self.last_solve_step >= self.solving_delay:
            if self.current_step < len(self.solver_steps):
                step = self.solver_steps[self.current_step]
                row, col, value = step
                
                if not self.valid_entries[row][col] and not self.original_board[row][col]:
                    self.game_board[row][col] = value
                
                self.current_step += 1
                self.last_solve_step = current_time
            else:
                self.solving_animation = False
                self.errors.clear()
                self.clashing_cells.clear()
                delattr(self, 'solver_steps')
    
    def solve_game(self):
        self.solving_animation = True
        self.last_solve_step = pygame.time.get_ticks()
    
    def draw_game(self):
        self.screen.fill(c.PASTEL_BLUE)
        self.draw_grid()
        self.back_button.draw(self.screen)
        self.solve_button.draw(self.screen)
        self.reset_button.draw(self.screen)
        
        if self.start_time:
            self.elapsed_time = time.time() - self.start_time
        minutes = int(self.elapsed_time // 60)
        seconds = int(self.elapsed_time % 60)
        timer_text = f"Time: {minutes:02d}:{seconds:02d}"
        timer_surface = self.font.render(timer_text, True, c.BLACK)
        self.screen.blit(timer_surface, (c.WINDOW_WIDTH//2 - 50, 30))
    
    def handle_cell_click(self, pos):
      grid_width = c.GRID_SIZE * c.CELL_SIZE
      grid_height = c.GRID_SIZE * c.CELL_SIZE
      start_x = (c.WINDOW_WIDTH - grid_width) // 2
      start_y = (c.WINDOW_HEIGHT - grid_height) // 2
      
      if (start_x <= pos[0] <= start_x + grid_width and 
          start_y <= pos[1] <= start_y + grid_height):
          col = (pos[0] - start_x) // c.CELL_SIZE
          row = (pos[1] - start_y) // c.CELL_SIZE
          if self.original_board[row][col] == 0:
              self.selected_cell = (row, col)
          else:
              self.selected_cell = None

    def reset_game(self):
      self.game_board = self.original_board.copy()
      self.start_time = time.time()
      self.selected_cell = None
      self.errors.clear() 
    
    def return_to_menu(self):
        self.current_screen = "menu"
        self.selected_cell = None
        self.game_board = None
        self.original_board = None
        self.start_time = None
        self.elapsed_time = 0
        self.errors.clear()
        self.clashing_cells.clear()
        if hasattr(self, 'solver_steps'):
            delattr(self, 'solver_steps')
        self.solving_animation = False

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    if self.current_screen == "menu":
                        for button in self.menu_buttons:
                            if button.rect.collidepoint(mouse_pos):
                                self.start_game(button.text)
                    
                    elif self.current_screen == "game":
                        if self.back_button.rect.collidepoint(mouse_pos):
                            self.return_to_menu()
                        elif self.reset_button.rect.collidepoint(mouse_pos):
                            self.reset_game()
                        elif self.solve_button.rect.collidepoint(mouse_pos):
                            self.solve_game()
                        else:
                            self.handle_cell_click(mouse_pos)
                    
                    elif self.current_screen == "congratulations":
                        continue_button = self.draw_congratulations()
                        if continue_button.rect.collidepoint(mouse_pos):
                            self.return_to_menu()
                
                elif event.type == pygame.KEYDOWN and self.current_screen == "game" and not self.solving_animation:
                    self.handle_key_input(event.key)
            
            if self.current_screen == "menu":
                self.draw_menu()
            elif self.current_screen == "game":
                if self.solving_animation:
                    self.solve_step()
                self.draw_game()
            elif self.current_screen == "congratulations":
                self.draw_game()
                self.draw_congratulations()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()