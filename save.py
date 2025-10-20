from generator import NonogramGenerator
from solver import NonogramSolver
import time
import os

os.makedirs("problem", exist_ok=True)

generator = NonogramGenerator(40, 40, 0.5)

file_name = f"problem/puzzle3.txt"
for _ in range(1):
    generator.generate_solution()
    row_hint, col_hint = generator.get_hints()
    
    with open(file_name, "a", encoding="utf-8") as f:
        f.write("Row:\n")
        for r in row_hint:
            f.write(" ".join(map(str, r)) + "\n")
        f.write("Col:\n")
        for c in col_hint:
            f.write(" ".join(map(str, c)) + "\n")
    