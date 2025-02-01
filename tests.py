import unittest
import numpy as np

from io import StringIO
from board_generator import SudokuBoardGenerator
from solver import SudokuSolver
from game import SudokuGame

class TestSudokuBoard(unittest.TestCase):
    def setUp(self):
        self.generator = SudokuBoardGenerator()
        
    def test_board_generation(self):
        print("\nTesting board generation...")
        board = self.generator.generate("easy")
        non_zero_count = np.count_nonzero(board)
        print(f"Generated board has {non_zero_count} filled cells")
        self.assertEqual(board.shape, (9, 9))
        self.assertTrue(45 <= non_zero_count <= 55, 
                       f"Expected 45-55 filled cells for easy difficulty, got {non_zero_count}")
        
    def test_board_validity(self):
        print("\nTesting board validity...")
        board = self.generator.generate("medium")
        
        def check_unit(unit):
            numbers = [x for x in unit if x != 0]
            return len(numbers) == len(set(numbers))
        
        # Check rows
        for row in board:
            self.assertTrue(check_unit(row))
            print(f"Row check passed: {row}")
            
        # Check columns
        for col in board.T:
            self.assertTrue(check_unit(col))
            print(f"Column check passed: {col}")
            
        # Check 3x3 boxes
        for i in range(0, 9, 3):
            for j in range(0, 9, 3):
                box = board[i:i+3, j:j+3].flatten()
                self.assertTrue(check_unit(box))
                print(f"Box check passed at position ({i},{j})")

class TestSudokuSolver(unittest.TestCase):
    def setUp(self):
        self.test_board = np.array([
            [5,3,0,0,7,0,0,0,0],
            [6,0,0,1,9,5,0,0,0],
            [0,9,8,0,0,0,0,6,0],
            [8,0,0,0,6,0,0,0,3],
            [4,0,0,8,0,3,0,0,1],
            [7,0,0,0,2,0,0,0,6],
            [0,6,0,0,0,0,2,8,0],
            [0,0,0,4,1,9,0,0,5],
            [0,0,0,0,8,0,0,7,9]
        ])
        self.solver = SudokuSolver(self.test_board.copy())
        
    def test_solving_steps(self):
        print("\nTesting solving steps...")
        steps = self.solver.get_solving_steps()
        print(f"Found {len(steps)} solving steps")
        self.assertTrue(len(steps) > 0)
        
        # Print first few steps
        print("First 5 solving steps:")
        for i, (row, col, value) in enumerate(steps[:5]):
            print(f"Step {i+1}: Place {value} at position ({row},{col})")
            
    def test_complete_solve(self):
        print("\nTesting complete solve...")
        initial_zeros = np.count_nonzero(self.solver.grid == 0)
        print(f"Initial empty cells: {initial_zeros}")
        
        # Create a modified version of solve() without display
        def solve_without_display(solver):
            while True:
                if not (solver.single_candidate() or solver.hidden_single() or solver.naked_pairs()):
                    break
                if solver.is_solved():
                    return True
            if not solver.is_solved():
                return solver.backtrack_solve()
            return solver.is_solved()
        
        solved = solve_without_display(self.solver)
        self.assertTrue(solved)
        
        final_zeros = np.count_nonzero(self.solver.grid == 0)
        print(f"Final empty cells: {final_zeros}")
        self.assertEqual(final_zeros, 0)
        
        # Verify solution
        for i in range(9):
            row_sum = np.sum(self.solver.grid[i,:])
            col_sum = np.sum(self.solver.grid[:,i])
            self.assertEqual(row_sum, 45)  # Sum of 1-9
            self.assertEqual(col_sum, 45)
            print(f"Row {i} sum: {row_sum}, Column {i} sum: {col_sum}")

class TestGameIntegration(unittest.TestCase):
    def setUp(self):
        self.game = SudokuGame()
        
    def test_game_initialization(self):
        print("\nTesting game initialization...")
        self.game.start_game("easy")
        
        # Check board state
        self.assertIsNotNone(self.game.game_board)
        self.assertIsNotNone(self.game.original_board)
        self.assertEqual(self.game.current_screen, "game")
        
        filled_cells = np.count_nonzero(self.game.game_board)
        print(f"Initial board has {filled_cells} filled cells")
        print(f"Current screen: {self.game.current_screen}")
        
    def test_cell_validation(self):
        print("\nTesting cell validation...")
        self.game.start_game("easy")
        
        # Test valid move
        test_row, test_col = 0, 0
        while self.game.original_board[test_row, test_col] != 0:
            test_col += 1
            if test_col == 9:
                test_col = 0
                test_row += 1
        
        print(f"Testing valid move at position ({test_row},{test_col})")
        
        # Find a valid number for this position
        valid_num = None
        for num in range(1, 10):
            if self.game.validate_cell(test_row, test_col, num):
                valid_num = num
                break
        
        self.assertIsNotNone(valid_num)
        print(f"Found valid number {valid_num} for position ({test_row},{test_col})")
        
        # Test invalid move
        print("Testing invalid move detection...")
        row_nums = set(self.game.game_board[test_row])
        invalid_num = next(num for num in row_nums if num != 0)
        is_valid = self.game.validate_cell(test_row, test_col, invalid_num)
        self.assertFalse(is_valid)
        print(f"Invalid move detected: {invalid_num} at position ({test_row},{test_col})")
        
    def test_game_reset(self):
        print("\nTesting game reset functionality...")
        self.game.start_game("easy")
        original_board = self.game.game_board.copy()
        
        # Make some moves
        empty_pos = np.where(self.game.game_board == 0)
        if len(empty_pos[0]) > 0:
            row, col = empty_pos[0][0], empty_pos[1][0]
            self.game.game_board[row, col] = 5
            
        # Reset game
        self.game.reset_game()
        
        # Verify reset
        np.testing.assert_array_equal(self.game.game_board, original_board)
        self.assertIsNone(self.game.selected_cell)
        self.assertEqual(len(self.game.errors), 0)
        print("Game reset successful")

def run_tests():
    # Create a test suite
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSudokuBoard))
    suite.addTest(unittest.makeSuite(TestSudokuSolver))
    suite.addTest(unittest.makeSuite(TestGameIntegration))
    
    # Create a runner that will store the output
    stream = StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    
    # Run the tests
    result = runner.run(suite)
    
    # Print the output
    print("\nTest Results:")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("=" * 70)
    
    # Print detailed output
    print("\nDetailed Test Output:")
    print(stream.getvalue())

if __name__ == '__main__':
    run_tests()