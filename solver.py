class NonogramSolver:
    def __init__(self):
        self.row_size = 5   # 행 개수
        self.col_size = 5   # 열 개수
        self.row_hint = [[1, 3], [1, 1, 1], [1, 1, 1], [1, 1, 1], [1, 3]]
        self.col_hint = [[5], [0], [5], [1, 1], [5]]
        self.board = [[0 for _ in range(self.col_size)] for _ in range(self.row_size)]
        self.difficulty = 0
        
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
        self.board = [[0 for _ in range(self.col_size)] for _ in range(self.row_size)]
        print(f"Set the Problem with Row: {self.row_size}, Col: {self.col_size}")
        
    def _fill_line(self, hint, line):
        """모든 행과 열에 대해 교차점 알고리즘을 적용하여 확정되는 칸을 채운다."""
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
    
    def _match_hint(self, hint, line):
        """주어진 line이 hint를 만족하는지 확인한다."""
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
    
    def _is_correct(self):
        """현재 board 상태가 hint를 만족하는지 확인한다."""
        row_hint = self.row_hint
        col_hint = self.col_hint
        board = self.board
        
        for r in range(self.col_size):
            if not self._match_hint(row_hint[r], board[r]):
                return False
        for c in range(self.row_size):
            col = [board[r][c] for r in range(self.row_size)]
            if not self._match_hint(col_hint[c], col):
                return False
        return True
    
    def _get_all_solutions(self, length, hint):
        """주어진 힌트를 만족하는 모든 가능한 line을 반환한다."""
        
        results = []

        def find_solutions(current_line, hint_index, line_index):
            # 성공 조건: 모든 힌트를 사용했고, 줄의 끝에 도달함
            if hint_index == len(hint):
                results.append(current_line[:])
                return

            # 실패 조건: 줄의 끝을 넘어감
            if line_index >= length:
                return

            # 현재 힌트를 적용할 수 있는 경우
            hint_size = hint[hint_index]
            
            # 1. 현재 위치에서 블록을 놓는 경우
            if line_index + hint_size <= length:
                # 다음 힌트와의 간격을 고려하여 블록을 놓을 수 있는지 확인
                # 블록 뒤에 적어도 하나의 공백이 필요
                temp_line = current_line[:]
                for i in range(hint_size):
                    temp_line[line_index + i] = 1
                find_solutions(temp_line, hint_index + 1, line_index + hint_size + 1)

            # 2. 현재 위치를 건너뛰는 경우
            find_solutions(current_line, hint_index, line_index + 1)

        initial_row = [-1] * length
        find_solutions(initial_row, 0, 0)
                
        return results
            
    def _infer(self, hint, line):
        """
        hint로부터 가능한 모든 줄의 상태를 얻고, 그 중 현재 line을 만족하는 줄들만 남긴다.
        현재 line을 만족하는 solution들로부터 공통된 칸들을 찾아 추가적인 정보를 반영한 new_line을 반환한다.
        """
        
        length = len(line)
        solutions = self._get_all_solutions(length, hint)
        
        possible_solutions = []
        for solution in solutions:
            is_match = True
            # 현재 줄의 상태를 순회하며 각 해답과 비교
            for i in range(length):
                # 미확정 상태(0)가 아닌 경우에만 비교
                if line[i] != 0 and line[i] != solution[i]:
                    is_match = False
                    break # 일치하지 않으면 다음 해답으로
            
            if is_match:
                possible_solutions.append(solution)
        
        new_line = line[:]
        for i in range(length):
            if line[i] == 0:
                value = possible_solutions[0][i]
                is_common = True
                
                for solution in possible_solutions[1:]:
                    if solution[i] != value:
                        is_common = False
                        break
                    
                if is_common:
                    new_line[i] = value

        return new_line
        
    def solve_problem(self, log=True):
        print("Solving the problem...")
        count = 0
        row_hint = self.row_hint
        col_hint = self.col_hint
        board = self.board
        
        for r in range(self.col_size):
            temp = self._fill_line(row_hint[r], board[r])
            board[r] = temp
        if log:
            print("Fill line: row")
            self.print_board()
        
        for c in range(self.row_size):
            temp = self._fill_line(col_hint[c], [board[r][c] for r in range(self.row_size)])
            for r in range(self.row_size):
                board[r][c] = temp[r]
        if log:
            print("Fill line: col")
            self.print_board()

        while True:
            count += 1
            prev_board = [row[:] for row in board]
            
            for r in range(self.col_size):
                temp = self._infer(row_hint[r], board[r])
                board[r] = temp
            for c in range(self.row_size):
                temp = self._infer(col_hint[c], [board[r][c] for r in range(self.row_size)])
                for r in range(self.row_size):
                    board[r][c] = temp[r]
            if log:
                print("Iteration:", count)
                self.print_board()
                
            if self._is_correct():
                print("Problem solved!")
                self.difficulty = count
                return True
            if prev_board == board:
                print("Cannot solve the problem.")
                self.difficulty = None
                return False
                
        