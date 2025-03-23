def solve(hint, temp, length): # num번째 row 또는 column을 solve
    require = sum(hint) + len(hint) - 1
    if require <= length:
        diff = length - require
        pr = 0
        for term in hint:
            if term > diff:
                temp[pr + diff:pr + term] = [1] * (term - diff)
            pr += term + 1
    return temp
    
def match_hint(hint, temp): # hint를 만족하는지 확인하는 함수
    groups = []
    count = 0
    for entry in temp:
        if entry == 1:
            count += 1
        elif count > 0:
            groups.append(count)
            count = 0
    if count > 0:
        groups.append(count)
    return groups == hint
    
def solvable(hint, temp, length):
    empty_list = [i for i in range(length) if temp[i] == 0]
        
    def backtrack(index):
        if index == len(empty_list):
            return match_hint(hint, temp)
        
        i = empty_list[index]
        temp[i] = 1
        if backtrack(index + 1):
            return True
        temp[i] = -1
        if backtrack(index + 1):
            return True
        return False
    
    return backtrack(0) 
    
def exclude(hint, temp, length):
    empty_list = [i for i in range(length) if temp[i] == 0]
    for i in empty_list:
        temp2 = [e for e in temp]
        temp2[i] = 1
        if not solvable(hint, temp2, length):
            temp[i] = -1
            continue
            
        temp2 = [e for e in temp]
        temp2[i] = -1
        if not solvable(hint, temp2, length):
            temp[i] = 1
            continue
    return temp

def duplication_break(solution, r, c):
    zero_list = []
    for i in range(r):
        for j in range(c):
            if solution[i][j] == 0: zero_list.append((i, j))
    
    for entry in zero_list:
        i, j = entry
        temp_row = [e for e in solution[i]]
        temp_col = [solution[k][j] for k in range(r)]
        temp_row[j] = 1
        temp_col[i] = 1
        if solvable(rows[i], temp_row, c) and solvable(cols[j], temp_col, r):
            solution[i][j] = 1
        
    zero_list = []
    for i in range(r):
        for j in range(c):
            if solution[i][j] == 0: zero_list.append((i, j))
            
    for entry in zero_list:
        i, j = entry
        temp_row = [e for e in solution[i]]
        temp_col = [solution[k][j] for k in range(r)]
        temp_row[j] = -1
        temp_col[i] = -1
        if solvable(rows[i], temp_row, c) and solvable(cols[j], temp_col, r):
            solution[i][j] = -1

def solved():
    for row in solution:
        if 0 in row:
            return False
    return True

def print_solution(solution, option):
    for row in solution:
        for entry in row:
            if option == 'shape': print('■' if entry == 1 else '□', end='')
            elif option == 'num': print(f"{entry:2}", end=' ')
        print()
    print('---------------------------------')
 
def solve_nonogram(solution, rows, cols):
    r = len(rows)
    c = len(cols)
    
    # solve() 단계
    for i in range(r):
        temp = solve(rows[i], [e for e in solution[i]], c)
        solution[i] = temp
    for i in range(c):
        temp = solve(cols[i], [solution[j][i] for j in range(r)], r)
        for j in range(r): solution[j][i] = temp[j]
    print_solution(solution, "num") # solve() 적용 후
    
    # exclude() 반복 단계
    while (not solved()):
        temp_solution = [[e for e in row] for row in solution]
        for i in range(r):
            temp = exclude(rows[i], [e for e in temp_solution[i]], c)
            temp_solution[i] = temp
        for i in range(c):
            temp = exclude(cols[i], [temp_solution[j][i] for j in range(r)], r)
            for j in range(r): temp_solution[j][i] = temp[j]
        if temp_solution == solution:
            break
        else: solution = [[e for e in row] for row in temp_solution]
        print_solution(solution, "num")
    
    # duplication_break() 단계
    duplication_break(solution, r, c)
    print_solution(solution, "num")
    
    return solution
    
####################################################
import re

def parse(line):
    pattern = re.compile(r'\[(.*?)\]')
    matches = pattern.findall(line)
    
    parsed_list = []
    for match in matches:
        parsed_list.append([int(num) for num in match.split(',')])
    
    return parsed_list

def load_problems():
    with open('nonogram_problems.txt', 'r') as file:
        lines = file.readlines()
    
    problems = []
    i = 0
    while i < len(lines):
        rows = []
        cols = []
        answer = []
        
        rows = parse(lines[i].strip())
        i += 1
        cols = parse(lines[i].strip())
        i += 1
        answer = parse(lines[i].strip())
        i += 1
        
        problems.append((rows, cols, answer))
    
    return problems

problems = load_problems()
for problem in problems:
    rows, cols, answer = problem
    r = len(rows)
    c = len(cols)
    solution = [[0 for _ in range(c)] for _ in range(r)]
        
    solution = solve_nonogram(solution, rows, cols)
    print_solution(solution, "shape")
    print_solution(answer, "shape")
    print('Correct!' if solution == answer else 'Incorrect!')
    
# solvable test
# print(solvable([3, 1, 1], [1, 1, 1, -1, -1, 1, -1, 1, -1, -1, -1, 0, -1, -1, -1], 15))