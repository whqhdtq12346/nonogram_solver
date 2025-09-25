from generator import NonogramGenerator
from solver import NonogramSolver
import time

generator = NonogramGenerator(40, 40, 0.5)
problem_list = []
diff_list = []
start_time = time.time()
for i in range(10):
    generator.generate_solution()
    # generator.print_solution()
    row_hint, col_hint = generator.get_hints()
    diff_list.append(generator.difficulty)
    problem_list.append((row_hint, col_hint))
end_time = time.time()

execution_time = end_time - start_time
avg_diff = sum(diff_list) / len(diff_list)
print(f"Execution time: {execution_time}sec")
print(f"Average difficulty: {avg_diff}")
input()

solver = NonogramSolver()
start_time = time.time()
for i, problem in enumerate(problem_list):
    row_hint, col_hint = problem
    solver.set_problem(row_hint, col_hint)
    solver.solve_problem(log=False)
end_time = time.time()

execution_time = end_time - start_time
print(f"Execution time: {execution_time}sec")