"""
Main CLI interface for Game of Life simulator.
"""

import sys
import os
import time
import logging
from GameOfLife.board import Board
from GameOfLife.simulator import Simulator
from GameOfLife.pattern_parser import PatternParser
from GameOfLife.metaprogramming import RuleRegistry
from GameOfLife.exceptions import GameOfLifeError


def setup_logging():
    """Configure logging to file and console."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('game_of_life.log'),
            logging.StreamHandler()
        ]
    )


def clear_screen():
    """Clear terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def display_board_animated(board: Board, clear: bool = True):
    """Display board with optional screen clearing."""
    if clear:
        clear_screen()
    
    print(f"\nGeneration: {board.generation}")
    print(f"Alive cells: {board.count_alive()}")
    print("-" * (board.width + 2))
    print(board.to_string())
    print("-" * (board.width + 2))


def main_menu():
    """Display main menu and get user choice."""
    print("\n" + "=" * 60)
    print("CONWAY'S GAME OF LIFE SIMULATOR".center(60))
    print("=" * 60)
    print("\n1. Create new blank board")
    print("2. Load pattern from file")
    print("3. Use predefined pattern")
    print("4. Exit")
    
    choice = input("\nSelect option (1-4): ").strip()
    return choice


def simulation_menu():
    """Display simulation menu."""
    print("\n--- Simulation Options ---")
    print("1. Run for N generations")
    print("2. Run until stable")
    print("3. Step one generation")
    print("4. Display current state")
    print("5. Save current state to file")
    print("6. Show statistics")
    print("7. Change rules")
    print("8. Back to main menu")
    
    choice = input("\nSelect option (1-8): ").strip()
    return choice


def get_board_size():
    """Prompt user for board dimensions."""
    while True:
        try:
            width = int(input("Enter board width (10-100): "))
            height = int(input("Enter board height (10-100): "))
            
            if 10 <= width <= 100 and 10 <= height <= 100:
                return width, height
            else:
                print("Dimensions must be between 10 and 100")
        except ValueError:
            print("Please enter valid numbers")


def create_predefined_pattern(board: Board):
    """Create a predefined pattern on the board."""
    print("\nPredefined Patterns:")
    print("1. Glider")
    print("2. Blinker")
    print("3. Toad")
    print("4. Beacon")
    print("5. Pulsar")
    
    choice = input("\nSelect pattern (1-5): ").strip()
    
    # Place pattern in center
    center_row = board.height // 2
    center_col = board.width // 2
    
    if choice == '1':
        # Glider
        cells = [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
        for r, c in cells:
            board.set_cell(center_row + r, center_col + c, 1)
    
    elif choice == '2':
        # Blinker
        cells = [(0, 0), (0, 1), (0, 2)]
        for r, c in cells:
            board.set_cell(center_row + r, center_col + c, 1)
    
    elif choice == '3':
        # Toad
        cells = [(0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2)]
        for r, c in cells:
            board.set_cell(center_row + r, center_col + c, 1)
    
    elif choice == '4':
        # Beacon
        cells = [(0, 0), (0, 1), (1, 0), (2, 3), (3, 2), (3, 3)]
        for r, c in cells:
            board.set_cell(center_row + r, center_col + c, 1)
    
    elif choice == '5':
        # Pulsar
        cells = [
            (0, 2), (0, 3), (0, 4), (0, 8), (0, 9), (0, 10),
            (2, 0), (2, 5), (2, 7), (2, 12),
            (3, 0), (3, 5), (3, 7), (3, 12),
            (4, 0), (4, 5), (4, 7), (4, 12),
            (5, 2), (5, 3), (5, 4), (5, 8), (5, 9), (5, 10),
            (7, 2), (7, 3), (7, 4), (7, 8), (7, 9), (7, 10),
            (8, 0), (8, 5), (8, 7), (8, 12),
            (9, 0), (9, 5), (9, 7), (9, 12),
            (10, 0), (10, 5), (10, 7), (10, 12),
            (12, 2), (12, 3), (12, 4), (12, 8), (12, 9), (12, 10),
        ]
        for r, c in cells:
            if center_row + r < board.height and center_col + c < board.width:
                board.set_cell(center_row + r, center_col + c, 1)
    
    print(f"Pattern created!")


def select_rules():
    """Let user select evolution rules."""
    available_rules = RuleRegistry.list_rules()
    
    print("\nAvailable rule sets:")
    for i, rule in enumerate(available_rules, 1):
        print(f"{i}. {rule}")
    
    while True:
        try:
            choice = int(input(f"\nSelect rules (1-{len(available_rules)}): "))
            if 1 <= choice <= len(available_rules):
                return available_rules[choice - 1]
        except ValueError:
            pass
        print("Invalid choice")


def main():
    """Main entry point for Game of Life CLI."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    board = None
    simulator = None
    
    try:
        while True:
            choice = main_menu()
            
            if choice == '1':
                # Create blank board
                width, height = get_board_size()
                board = Board(width, height)
                print(f"\nCreated {width}x{height} blank board")
                
                # Ask if user wants to add pattern
                if input("Add a predefined pattern? (y/n): ").lower() == 'y':
                    create_predefined_pattern(board)
                
                simulator = Simulator(board)
                display_board_animated(board, clear=False)
            
            elif choice == '2':
                # Load from file
                filename = input("\nEnter pattern file path: ").strip()
                
                try:
                    width, height = get_board_size()
                    board = Board(width, height)
                    board.load_pattern(filename)
                    simulator = Simulator(board)
                    print(f"Loaded pattern from {filename}")
                    display_board_animated(board, clear=False)
                except Exception as e:
                    print(f"Error loading pattern: {e}")
                    continue
            
            elif choice == '3':
                # Predefined pattern
                width, height = get_board_size()
                board = Board(width, height)
                create_predefined_pattern(board)
                simulator = Simulator(board)
                display_board_animated(board, clear=False)
            
            elif choice == '4':
                print("\nGoodbye!")
                break
            
            else:
                print("Invalid choice")
                continue
            
            # Simulation loop
            if simulator:
                while True:
                    sim_choice = simulation_menu()
                    
                    if sim_choice == '1':
                        # Run N generations
                        try:
                            n = int(input("Number of generations: "))
                            animate = input("Animate? (y/n): ").lower() == 'y'
                            
                            if animate:
                                def callback(b, gen):
                                    display_board_animated(b)
                                    time.sleep(0.1)  # Delay between frames
                                
                                simulator.run(n, callback=callback)
                            else:
                                simulator.run(n)
                                display_board_animated(simulator.board, clear=False)
                            
                        except ValueError:
                            print("Invalid number")
                    
                    elif sim_choice == '2':
                        # Run until stable
                        max_gen = int(input("Maximum generations (default 1000): ") or "1000")
                        final_board, stability = simulator.run_until_stable(max_gen)
                        display_board_animated(final_board, clear=False)
                        print(f"\nStability: {stability}")
                    
                    elif sim_choice == '3':
                        # Step once
                        simulator.step()
                        display_board_animated(simulator.board, clear=False)
                    
                    elif sim_choice == '4':
                        # Display current state
                        display_board_animated(simulator.board, clear=False)
                    
                    elif sim_choice == '5':
                        # Save to file
                        filename = input("Enter filename to save: ").strip()
                        name = input("Pattern name (optional): ").strip() or None
                        PatternParser.save_pattern(filename, simulator.board, name)
                        print(f"Saved to {filename}")
                    
                    elif sim_choice == '6':
                        # Statistics
                        stats = simulator.get_statistics()
                        print("\n--- Statistics ---")
                        for key, value in stats.items():
                            print(f"{key}: {value}")
                    
                    elif sim_choice == '7':
                        # Change rules
                        new_rule = select_rules()
                        simulator = Simulator(simulator.board, new_rule)
                        print(f"Changed to {new_rule} rules")
                    
                    elif sim_choice == '8':
                        # Back to main menu
                        break
                    
                    else:
                        print("Invalid choice")
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    
    except GameOfLifeError as e:
        logger.error(f"Game of Life error: {e}")
        print(f"\nError: {e}")
    
    except Exception as e:
        logger.exception("Unexpected error")
        print(f"\nUnexpected error: {e}")


if __name__ == "__main__":
    main()