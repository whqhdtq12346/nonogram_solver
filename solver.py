class NonogramSolver:
    def __init__(self):
        self.row_num = 5   # 행 개수
        self.col_num = 5   # 열 개수
        self.row_hint = [[1, 3], [1, 1, 1], [1, 1, 1], [1, 1, 1], [1, 3]]
        self.col_hint = [[5], [0], [5], [1, 1], [5]]
        self.board = [[0 for _ in range(self.col_num)] for _ in range(self.row_num)]
        self.row_solutions = [[] for _ in range(self.row_num)]
        self.col_solutions = [[] for _ in range(self.col_num)]
        self.difficulty = 0
        
    def print_board(self):
        board = self.board
        for r, row in enumerate(board):
            hint_str = str(self.row_hint[r]).rjust(int(1.5 * self.col_num))
            print(hint_str, end=' ')
            print(''.join(['■' if val == 1 else '□' if val == -1 else '?' for val in row])) 
    
    def set_problem(self, row_hint, col_hint):
        self.row_num = len(row_hint)
        self.col_num = len(col_hint)
        self.row_hint = row_hint
        self.col_hint = col_hint
        self.board = [[0 for _ in range(self.col_num)] for _ in range(self.row_num)]
        self.row_solutions = [[] for _ in range(self.row_num)]
        self.col_solutions = [[] for _ in range(self.col_num)]
        print(f"Set the Problem with Row: {self.row_num}, Col: {self.col_num}")
        
    def _fill_line(self, hint, line):
        """모든 행과 열에 대해 교차점 알고리즘을 적용하여 확정되는 칸을 채운다."""
        length = len(line)
        if hint == [0]:
            return [-1 for _ in range(length)]
        
        if line == [-1]*length:
            return line
        
        # 시작 또는 끝 부분에 [0]으로 인해 사라진 line이 있을 경우 그 부분을 제외
        start = 0
        while line[start] == -1:
            start += 1
        end = length
        while line[end-1] == -1:
            end -= 1
        length = end - start 
        
        require = sum(hint) + len(hint) - 1
        new_line = line[:]
        if require <= length:
            diff = length - require
            for term in hint:
                if term > diff:
                    for i in range(start + diff, start + term):
                        new_line[i] = 1
                start += term + 1
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
        
        for r in range(self.row_num):
            if not self._match_hint(row_hint[r], board[r]):
                return False
        for c in range(self.col_num):
            col = [board[r][c] for r in range(self.row_num)]
            if not self._match_hint(col_hint[c], col):
                return False
        return True
    
    def _get_all_solutions(self, length, hint, line):
        """주어진 힌트(hint)와 현재 줄의 상태(line)를 만족하는 모든 가능한 solution을 반환한다."""
        
        results = []

        def find_solutions(current_line, hint_index, line_index):
            # 성공 조건: 모든 힌트를 사용했고, 줄의 끝에 도달함
            if hint_index == len(hint):
                # 남은 칸 중 1이 있는지 확인
                is_valid = True
                for i in range(line_index, length):
                    if line[i] == 1:
                        is_valid = False
                        break
                if is_valid:
                    results.append(current_line[:])
                return

            # 실패 조건: 줄의 끝을 넘어갔거나, 기존 줄의 상태와 맞지 않을 경우
            if line_index >= length:
                return
            
            # 1. 현재 위치에서 블록을 놓는 경우
            hint_size = hint[hint_index]
            if line_index + hint_size <= length:
                temp_line = current_line[:]
                place = True
                
                # 블록 내에 확정된 -1이 있는지 확인
                for i in range(hint_size):
                    if line[line_index + i] == -1:
                        place = False
                        break
                
                # 블록 뒤에 -1이 올 수 있는지 확인
                if line_index + hint_size < length and line[line_index + hint_size] == 1:
                    place = False
                
                if place:
                    for i in range(hint_size):
                        temp_line[line_index + i] = 1
                    find_solutions(temp_line, hint_index + 1, line_index + hint_size + 1)

            # 2. 현재 위치를 건너뛰는 경우
            # 현재 위치가 1로 확정되지 않았을 때만 가능
            if line[line_index] != 1:
                find_solutions(current_line, hint_index, line_index + 1)

        initial_row = [-1] * length
        find_solutions(initial_row, 0, 0)
                
        return results
            
    def _infer(self, row, index):
        """
        Args:
            row: 추론할 line이 가로줄이면 True, 세로줄이면 False
            index: 추론할 line의 번호
        대상 line의 현재 가능한 solution들의 집합으로부터 공통된 칸들을 찾아 추가적인 정보를 반영한 new_line을 반환한다.
        """
        
        line = self.board[index] if row else [self.board[r][index] for r in range(self.row_num)]
        length = len(line)
        solutions = self.row_solutions[index] if row else self.col_solutions[index]
        
        new_line = line[:]
        for i in range(length):
            if line[i] == 0:
                value = solutions[0][i]
                is_common = True
                
                for solution in solutions[1:]:
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
        # 정보가 추가된 줄에 대해서만 infer를 수행
        row_infer_list = [False for _ in range(self.row_num)]
        col_infer_list = [False for _ in range(self.col_num)]
        
        # [0] 처리 단계
        for r in range(self.row_num):
            if row_hint[r] == [0]:
                board[r] = [-1 for _ in range(self.col_num)]
        
        for c in range(self.col_num):
            if col_hint[c] == [0]:
                for r in range(self.row_num):
                    board[r][c] = -1
        
        # fill_line 단계
        for r in range(self.row_num):
            row = board[r]
            temp = self._fill_line(row_hint[r], board[r])
            for c in range(self.col_num):
                if temp[c] != row[c]:
                    col_infer_list[c] = True
                    board[r][c] = temp[c]
        if log:
            print("Fill line: row")
            self.print_board()
        
        for c in range(self.col_num):
            col = [board[r][c] for r in range(self.row_num)]
            temp = self._fill_line(col_hint[c], col)
            for r in range(self.row_num):
                if temp[r] != col[r]:
                    row_infer_list[r] = True
                    board[r][c] = temp[r]
        if log:
            print("Fill line: col")
            self.print_board()

        solvable = True
        # infer 단계
        while True:
            count += 1
            prev_board = [row[:] for row in board]
            
            # Row infer
            for r in range(self.row_num):
                if not row_infer_list[r]:
                    continue
                
                row = board[r]
                self.row_solutions[r] = self._get_all_solutions(self.col_num, row_hint[r], row)
                if len(self.row_solutions[r]) == 0:
                    solvable = False
                    
                temp = self._infer(row=True, index=r)
                for c in range(self.col_num):
                    if temp[c] != row[c]:
                        col_infer_list[c] = True
                        board[r][c] = temp[c]
            row_infer_list = [False for _ in range(self.row_num)]
            
            # Column infer
            for c in range(self.col_num):
                if not col_infer_list[c]:
                    continue
                
                col = [board[r][c] for r in range(self.row_num)]
                self.col_solutions[c] = self._get_all_solutions(self.row_num, col_hint[c], col)
                if len(self.col_solutions[c]) == 0:
                    solvable = False
                
                temp = self._infer(row=False, index=c)
                for r in range(self.row_num):
                    if temp[r] != col[r]:
                        row_infer_list[r] = True
                        board[r][c] = temp[r]
            col_infer_list = [False for _ in range(self.col_num)]
            
            if log:
                print("Iteration:", count)
                self.print_board()
                # input()
                
            if self._is_correct():
                print("Problem solved!")
                self.difficulty = count
                self.row_solutions = None
                self.col_solutions = None
                return True
            if not solvable or prev_board == board:
                print("Cannot solve the problem.")
                self.difficulty = None
                self.row_solutions = None
                self.col_solutions = None
                return False
            
                
        