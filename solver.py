class NonogramSolver:
    def __init__(self):
        self.row_size = 5   # 행 개수
        self.col_size = 5   # 열 개수
        self.row_hint = [[1, 3], [1, 1, 1], [1, 1, 1], [1, 1, 1], [1, 3]]
        self.col_hint = [[5], [0], [5], [1, 1], [5]]
        self.board = [[0 for _ in range(self.col_size)] for _ in range(self.row_size)]
        
    def print_board(self):
        board = self.board
        for r, row in enumerate(board):
            hint_str = str(self.row_hint[r]).rjust(30)
            print(hint_str, end=' ')
            print(''.join(['■' if val == 1 else '□' if val == -1 else '?' for val in row])) 
    
    def set_problem(self, row_hint, col_hint):
        self.row_size = len(row_hint)
        self.col_size = len(col_hint)
        self.row_hint = row_hint
        self.col_hint = col_hint
        self.board = [[0] * self.col_size] * self.row_size
        
    def fill_line(self, hint, line):
        # 1단계: 모든 행과 열에 대해 교차점 알고리즘을 적용하여 확정되는 칸을 최대한 채운다.
        require = sum(hint) + len(hint) - 1
        length = len(line)
        new_line = line[:]
        if require <= length:
            diff = length - require
            pr = 0
            for term in hint:
                if term > diff:
                    for i in range(pr + diff, pr + term):
                        new_line[i] = 1
                pr += term + 1
        return new_line
    
    def match_hint(self, hint, line):
        # 주어진 line이 hint를 만족하는지 확인한다.
        groups = []
        count = 0
        for entry in line:
            if entry == 1:
                count += 1
            elif count > 0:
                groups.append(count)
                count = 0
        if count > 0 or len(groups) == 0:
            groups.append(count)
        return groups == hint
    
    def is_correct(self):
        # 현재 board 상태가 hint를 만족하는지 확인한다.
        row_hint = self.row_hint
        col_hint = self.col_hint
        board = self.board
        
        for r in range(self.col_size):
            if not self.match_hint(row_hint[r], board[r]):
                return False
        for c in range(self.row_size):
            col = [board[r][c] for r in range(self.row_size)]
            if not self.match_hint(col_hint[c], col):
                return False
        return True
    
    def solvable(self, hint, line):
        # 현재 line에서 아직 정해지지 않은 빈칸(0)들을 채우는 모든 경우를
        # 백트래킹으로 탐색하여 hint를 만족하는 해가 존재하는지 확인한다.
        # ex) hint = [2, 1] 이고, line = [0 -1 0 0 0] 이면 hint를 만족하는 경우가 존재하지 않으므로 False
        
        length = len(line)
        empty_list = [i for i in range(length) if line[i] == 0]
        new_line = line[:] 
        def backtrack(index):
            if index == len(empty_list):
                return self.match_hint(hint, new_line)
            
            i = empty_list[index]
            new_line[i] = 1
            if backtrack(index + 1):
                return True
            new_line[i] = -1
            if backtrack(index + 1):
                return True
            return False
        
        return backtrack(0)
    
    def infer(self, hint, line):
        # 현재 line에서 모든 빈칸(0)에 대해 임시로 칠하거나(1) 비우고(-1),
        # 이 상태에서 해가 존재하는지 solvable 함수로 확인한다.
        # 만약 해가 존재하지 않는다면 해당 칸은 확정적으로 비어있거나 칠해진다.
        
        length = len(line)
        empty_list = [i for i in range(length) if line[i] == 0]
        new_line = line[:]
        for i in empty_list:
            new_line[i] = 1
            if not self.solvable(hint, new_line):
                new_line[i] = -1
                continue
            
            new_line[i] = -1
            if not self.solvable(hint, new_line):
                new_line[i] = 1
                continue
            new_line[i] = 0
            
            
        return new_line
        
    def solve_problem(self):
        count = 0
        row_hint = self.row_hint
        col_hint = self.col_hint
        board = self.board
        
        for r in range(self.col_size):
            temp = self.fill_line(row_hint[r], board[r])
            board[r] = temp
        print("Fill line: row")
        self.print_board()
        for c in range(self.row_size):
            temp = self.fill_line(col_hint[c], [board[r][c] for r in range(self.row_size)])
            for r in range(self.row_size):
                board[r][c] = temp[r]
        print("Fill line: col")
        self.print_board()

        while True:
            count += 1
            print("Iteration:", count)
            
            for r in range(self.col_size):
                temp = self.infer(row_hint[r], board[r])
                board[r] = temp
            for c in range(self.row_size):
                temp = self.infer(col_hint[c], [board[r][c] for r in range(self.row_size)])
                for r in range(self.row_size):
                    board[r][c] = temp[r]
            
            self.print_board()
            if self.is_correct() or count >= 10:
                break

## Test ##
nonoSolver = NonogramSolver()
'''nonoSolver.set_problem(
[[1, 6, 5], [1, 1, 2, 1], [1, 1, 8], [1, 1, 2, 4], [1, 2, 3, 2], [1, 1, 1, 1, 2, 1, 1], [4, 3, 2, 2], [2, 1, 1], [1, 1, 1, 3], [2, 1, 1, 1, 4], [1, 1, 2, 2], [1, 3, 2], [2, 1, 5, 1], [1, 4, 3, 1], [1, 1, 1, 1, 1, 1]],
[[1, 3, 1, 4, 1], [1, 2, 1], [1, 2, 1, 1, 3], [2, 3, 1], [1, 1, 3, 2], [1, 4, 1, 1], [1, 1, 1, 1, 2, 2], [1, 1, 2, 1, 2], [2, 1, 1, 4], [2, 3, 3, 1], [1, 1, 3, 1, 3], [1, 2, 3, 2], [1, 2, 1, 2, 4], [1, 3, 1, 1, 1], [2, 4, 1, 2]]
)'''
nonoSolver.solve_problem()

# infer test
#print(nonoSolver.infer([4], [0,0,0,0,0]))
#print(nonoSolver.solvable([1, 2], [0,0,0,-1,0]))