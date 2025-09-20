from generator import NonogramGenerator
from solver import NonogramSolver

generator = NonogramGenerator(10, 10)
generator.generate_solution()
generator.print_solution()
row_hint, col_hint = generator.get_hints()
print(row_hint)
print(col_hint)

solver = NonogramSolver()
solver.set_problem(row_hint, col_hint)
solver.solve_problem()