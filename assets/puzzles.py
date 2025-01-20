from pathlib import Path
from dummy_kenken import Kenken

# Get the path to the kenken_puzzles directory
PUZZLES_DIR = Path(__file__).parent / "kenken_puzzles"

def load_puzzle(number: int) -> Kenken:
    """Load a puzzle from the assets/kenken_puzzles directory"""
    puzzle_file = PUZZLES_DIR / f"puzzle_{number}.txt"
    return Kenken(str(puzzle_file))

def puzzle0() -> Kenken:
    return load_puzzle(0)

def puzzle1() -> Kenken:
    return load_puzzle(1)

def puzzle2() -> Kenken:
    return load_puzzle(2)

def puzzle3() -> Kenken:
    return load_puzzle(3)
