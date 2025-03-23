rows = [[1, 1], [2, 2], [3], [2], [2]]
cols = [[2, 2], [4], [1], [2], [2]]
r = len(rows)
c = len(cols)
solution = [[0 for _ in range(r)] for _ in range(c)]

def solve_nonogram(rows, cols):
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
            temp[i] = 0
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
            
            temp2[i] = -1
            if not solvable(hint, temp2, length):
                temp[i] = 1
        return temp
            
            
        
    for i in range(r):
        temp = solve(rows[i], [e for e in solution[i]], c)
        solution[i] = temp
    for i in range(c):
        temp = solve(cols[i], [solution[j][i] for j in range(r)], r)
        for j in range(r): solution[j][i] = temp[j]
        
    for i in range(r):
        temp = exclude(rows[i], [e for e in solution[i]], c)
        solution[i] = temp
    for i in range(c):
        temp = exclude(cols[i], [solution[j][i] for j in range(r)], r)
        for j in range(r): solution[j][i] = temp[j]
        
solve_nonogram(rows, cols)
for row in solution:
    for entry in row:
        print(f"{entry:2}", end=' ')
    print()