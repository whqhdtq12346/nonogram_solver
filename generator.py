import random
from solver import NonogramSolver

class NonogramGenerator:
    def __init__(self, row_size, col_size, fill_ratio):
        self.row_size = row_size
        self.col_size = col_size
        self.solution = None
        self.row_hint = None
        self.col_hint = None
        self.fill_ratio = fill_ratio
        
    def generate_solution(self):
        print("Generating the problem...")
        board = [[0] * self.col_size for _ in range(self.row_size)]
        total_count = self.row_size * self.col_size
        
        target_count = int(total_count * self.fill_ratio)
        filled_count = 0 # 칠해진 칸(1) 수
        empty_count = 0 # 칠해지지 않은 칸(-1) 수
        border = set()
        
        random.seed()
        start_row, start_col = random.randint(0, self.row_size - 1), random.randint(0, self.col_size - 1)
        board[start_row][start_col] = 1
        filled_count += 1
        
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            r, c = start_row + dr, start_col + dc
            if 0 <= r < self.row_size and 0 <= c < self.col_size:
                border.add((r, c))
                
        while filled_count < target_count:
            # 남아있는 칸 수가 더 칠해야 할 칸 수와 같을 경우, 남은 칸들을 모두 칠하고 종료
            if total_count - empty_count == target_count:
                board = [[1 if cell == 0 else cell for cell in row] for row in board]
                break
                
            border_ratio = (len(border) ** 2 - 1) / (self.row_size * self.col_size)
            progress = filled_count / target_count
            fill_prob = 1.0 - border_ratio * progress
            
            r, c = random.choice(list(border))
            # print(f"위치: ({r}, {c}), 칠해질 확률: {fill_prob}")
            
            if random.random() < fill_prob:
                board[r][c] = 1
                filled_count += 1
                border.remove((r, c))
            
                for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.row_size and 0 <= nc < self.col_size:
                        if board[nr][nc] == 0:
                            border.add((nr, nc))
            else:
                board[r][c] = -1
                empty_count += 1
                border.remove((r, c))
            
            '''        
            print('Filled:', filled_count) 
            for r, row in enumerate(board):
                print(''.join(['■' if val == 1 else '□' if val == -1 else '?' for val in row]))
            input()
            '''
            
            
        board = [[-1 if cell == 0 else cell for cell in row] for row in board]
        self.solution = board
        self.row_hint = [self._get_hint_from_line(row) for row in self.solution]
        self.col_hint = [self._get_hint_from_line(col) for col in zip(*self.solution)]
        
        # 생성한 퍼즐이 유일해를 갖는지 확인
        solver = NonogramSolver()
        solver.set_problem(self.row_hint, self.col_hint)
        if not solver.solve_problem(log=False):
            return self.generate_solution()
        else:
            d = solver.difficulty
            print(f"Problem with difficulty {d} generated!")
        
    def _get_hint_from_line(self, line):
        hint = []
        count = 0
        for entry in line:
            if entry == 1:
                count += 1
            elif count > 0:
                hint.append(count)
                count = 0
        if count > 0: hint.append(count)
        return hint if len(hint) > 0 else [0]
    
    def get_hints(self):
        return self.row_hint, self.col_hint
    
    def print_solution(self):
        for r, row in enumerate(self.solution):
            hint_str = str(self.row_hint[r]).rjust(30)
            print(hint_str, end=' ')
            print(''.join(['■' if val == 1 else '□' if val == -1 else '?' for val in row]))