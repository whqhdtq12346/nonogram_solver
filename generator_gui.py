import pygame
import sys
from generator import NonogramGenerator

# 기본 설정
BUTTON_HEIGHT = 40
BUTTON_WIDTH = 150

WHITE = (240, 240, 240)
BLACK = (0, 0, 0)
BLUE = (200, 200, 255)
GRAY = (180, 180, 180)
DARK_GRAY = (80, 80, 80)

pygame.init()
font_18 = pygame.font.Font("font/NanumGothic.otf", 18)
font_22 = pygame.font.Font("font/NanumGothic.otf", 22)
font_36 = pygame.font.Font("font/NanumGothic.otf", 36)

class GeneratorGUI:
    def __init__(self):
        self.rows = 5
        self.cols = 5
        self.generator = None
        self.solution = None
        self.row_hint = []
        self.col_hint = []
        self.user_board = None
        
        # 메시지
        self.message = ""
        self.message_timer = 0
        
        # 드래그
        self.dragging = False
        self.drag_button = None
        self.drag_action = None
        self.last_drag_cell = None
        
        # GUI
        self.margin_left = 150
        self.margin_top = 150
        self.cell_size = 30
        self.font_size = 18
        self.start_time = None
        self.elapsed_time = 0
        self.timer_running = False
        
        # input
        self.active_input = None
        self.row_input = ""
        self.col_input = ""
        self.difficulty_level = "Normal"
        self.difficulty_value = None
        
        # 창 생성
        self.screen = pygame.display.set_mode((1200, 900))
        pygame.display.set_caption("Nonogram")

        # 버튼 정의
        self.buttons = {
            "Generate": pygame.Rect(975, 300, BUTTON_WIDTH, BUTTON_HEIGHT),
            "Solve": pygame.Rect(975, 350, BUTTON_WIDTH, BUTTON_HEIGHT),
            "Reset": pygame.Rect(975, 400, BUTTON_WIDTH, BUTTON_HEIGHT),
            "Check": pygame.Rect(975, 450, BUTTON_WIDTH, BUTTON_HEIGHT),
            "Back": pygame.Rect(975, 500, BUTTON_WIDTH, BUTTON_HEIGHT),
        }
        
    def draw_inputs(self):
        # row/col 입력창
        row_box = pygame.Rect(1025, 150, 100, 30)
        col_box = pygame.Rect(1025, 190, 100, 30)
        pygame.draw.rect(self.screen, GRAY if self.active_input == "row" else WHITE, row_box)
        pygame.draw.rect(self.screen, GRAY if self.active_input == "col" else WHITE, col_box)
        pygame.draw.rect(self.screen, BLACK, row_box, 2)
        pygame.draw.rect(self.screen, BLACK, col_box, 2)

        label_r = font_18.render("Row", True, BLACK)
        label_c = font_18.render("Col", True, BLACK)
        self.screen.blit(label_r, (975, 155))
        self.screen.blit(label_c, (975, 195))
        
        text_r = font_18.render(self.row_input if (self.active_input == "row") else (self.row_input or str(self.rows)), True, BLACK)
        text_c = font_18.render(self.col_input if (self.active_input == "col") else (self.col_input or str(self.cols)), True, BLACK)
        self.screen.blit(text_r, (row_box.x + 10, row_box.y + 5))
        self.screen.blit(text_c, (col_box.x + 10, col_box.y + 5))
        
        # 난이도 선택 버튼
        diff_options = ["Easy", "Normal", "Hard"]
        start_x = 925
        for i, opt in enumerate(diff_options):
            rect = pygame.Rect(start_x + i * 85, 230, 80, 30)
            color = BLUE if self.difficulty_level == opt else WHITE
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, BLACK, rect, 2)
            text_surface = font_18.render(opt, True, BLACK)
            text_rect = text_surface.get_rect(center=rect.center)
            self.screen.blit(text_surface, text_rect)
        
        

    def draw_board(self):
        self.screen.fill(WHITE)
        self.draw_inputs()
        
        if not self.user_board:
            msg = font_18.render("Press 'Generate' to create a puzzle.", True, BLACK)
            self.screen.blit(msg, (50, 50))
        else:
            self.cell_size = min(30, int(720 / max(self.rows, self.cols)))
            self.font_size = int(self.cell_size * 0.6)
            font_hint = pygame.font.Font("font/NanumGothic.otf", self.font_size) 
            
            # 행 힌트 (오른쪽 정렬)
            for i, hint in enumerate(self.row_hint):
                y = self.margin_top + (i + 0.2) * self.cell_size
                for k, num in enumerate(reversed(hint)):  # 오른쪽 끝부터 배치
                    text_surface = font_hint.render(str(num), True, BLACK)
                    hint_width = text_surface.get_width()
                    x = self.margin_left - 5 - (k + 1) * self.font_size * 1.1 + (self.font_size * 1.1 - hint_width) // 2
                    self.screen.blit(text_surface, (x, y))

            # 열 힌트 (세로 표시)
            for j, hint in enumerate(self.col_hint):
                for k, num in enumerate(reversed(hint)):
                    text_surface = font_hint.render(str(num), True, BLACK)
                    hint_width = text_surface.get_width()
                    x = self.margin_left + j * self.cell_size + (self.cell_size - hint_width) // 2
                    y = self.margin_top - 5 - (k + 1) * self.font_size * 1.1 
                    self.screen.blit(text_surface, (x, y))

            # 보드 셀
            for r in range(self.rows):
                for c in range(self.cols):
                    x = self.margin_left + c * self.cell_size
                    y = self.margin_top + r * self.cell_size
                    rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                    val = self.user_board[r][c]
                    color = WHITE
                    if val == 1:
                        color = DARK_GRAY
                    elif val == -1:
                        color = GRAY
                    pygame.draw.rect(self.screen, color, rect)
                    pygame.draw.rect(self.screen, BLACK, rect, 1)

            # 5칸마다 굵은 선
            board_width = self.cols * self.cell_size
            board_height = self.rows * self.cell_size
            for i in range(self.rows + 1):
                y = self.margin_top + i * self.cell_size
                width = 3 if i % 5 == 0 else 1
                pygame.draw.line(
                    self.screen, BLACK,
                    (self.margin_left, y),
                    (self.margin_left + board_width, y),
                    width
                )

            for j in range(self.cols + 1):
                x = self.margin_left + j * self.cell_size
                width = 3 if j % 5 == 0 else 1
                pygame.draw.line(
                    self.screen, BLACK,
                    (x, self.margin_top),
                    (x, self.margin_top + board_height),
                    width
                )

        # 타이머
        if self.start_time is not None and self.timer_running:
            self.elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000
        elif self.start_time is not None and not self.timer_running:
            pass
        minutes = self.elapsed_time // 60
        seconds = self.elapsed_time % 60
        time_str = f"{minutes:02}:{seconds:02}"
        time_surface = font_22.render(f"Time : {time_str}", True, BLACK)
        time_rect = time_surface.get_rect(center=(1050, 60))
        self.screen.blit(time_surface, time_rect)
        
        # 난이도 표시
        d = self.difficulty_value
        diff_text = f"Difficulty : {int(d) if d else '-'}"
        diff_surface = font_22.render(diff_text, True, BLACK)
        diff_rect = diff_surface.get_rect(center=(1050, 110))
        self.screen.blit(diff_surface, diff_rect)

        # 버튼
        for name, rect in self.buttons.items():
            pygame.draw.rect(self.screen, BLUE, rect)
            pygame.draw.rect(self.screen, BLACK, rect, 2)
            text_surface = font_18.render(name, True, BLACK)
            text_rect = text_surface.get_rect(center=rect.center)
            self.screen.blit(text_surface, text_rect)
            
        # 메시지
        if self.message and pygame.time.get_ticks() - self.message_timer < 3000:
            msg_surface = font_22.render(self.message, True, (0, 128, 0) if self.message == "Correct!" else (200, 0, 0))
            msg_rect = msg_surface.get_rect(center=(1050, 600))
            self.screen.blit(msg_surface, msg_rect)

        pygame.display.flip()

    def generate_puzzle(self):
        try:
            rows = int(self.row_input) if self.row_input else self.rows
            cols = int(self.col_input) if self.col_input else self.cols
            if rows < 3 or cols < 3:
                self.message = "Minimum size is 3x3!"
                self.message_timer = pygame.time.get_ticks()
                return
            self.rows, self.cols = rows, cols
        except ValueError:
            self.message = "Invalid input!"
            self.message_timer = pygame.time.get_ticks()
            return
        
        def average_difficulty(size):
            if size < 15: return 2
            elif size < 20: return 2.5
            elif size < 25: return 3
            elif size < 30: return 4
            elif size < 35: return 5
            elif size < 40: return 6
            else: return 7
            
        level = self.difficulty_level
        avg_diff = average_difficulty(min(self.rows, self.cols))
        d1, d2 = avg_diff * 0.75, avg_diff * 1.5
        
        if level == "Easy": fill_ratio = 0.7
        elif level == "Normal": fill_ratio = 0.3
        else: fill_ratio = 0.5
        
        self.message = "Generating puzzle..."
        pygame.display.flip()
        
        while True:
            self.generator = NonogramGenerator(self.rows, self.cols, fill_ratio)
            self.generator.generate_solution()
            
            d = self.generator.difficulty
            if (level == "Easy" and d <= d1) or (level == "Normal" and d1 < d < d2) or (level == "Hard" and d >= d2):
                self.row_hint, self.col_hint = self.generator.get_hints()
                self.solution = self.generator.solution
                self.user_board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
                self.difficulty_value = d
                break
                
        # 타이머 시작
        self.start_time = pygame.time.get_ticks()
        self.elapsed_time = 0
        self.timer_running = True

    def solve_puzzle(self):
        if self.solution is not None:
            self.user_board = [row[:] for row in self.solution]

    def reset_board(self):
        self.user_board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.start_time = pygame.time.get_ticks()
        self.elapsed_time = 0
        self.timer_running = True
        
    def check_answer(self):
        if self.solution is None:
            return
        temp = [[1 if cell == 1 else -1 for cell in row] for row in self.user_board]
        if temp == self.solution:
            self.message = "Correct!"
            self.user_board = [row[:] for row in self.solution]
            self.timer_running = False
        else:
            self.message = "Incorrect!"
        self.message_timer = pygame.time.get_ticks()
    
    def handle_input(self, event):
        """키보드 입력 처리"""
        if event.type == pygame.KEYDOWN and self.active_input:
            if event.key == pygame.K_BACKSPACE:
                if self.active_input == "row":
                    self.row_input = self.row_input[:-1]
                else:
                    self.col_input = self.col_input[:-1]
            elif event.unicode.isdigit():
                if self.active_input == "row":
                    self.row_input += event.unicode
                else:
                    self.col_input += event.unicode

        return None
    
    def handle_click(self, pos, button):
        x, y = pos
        
        # 버튼 클릭 처리
        for name, rect in self.buttons.items():
            if rect.collidepoint(pos):
                if name == "Generate":
                    self.generate_puzzle()
                elif name == "Solve":
                    self.solve_puzzle()
                elif name == "Reset":
                    self.reset_board()
                elif name == "Check":
                    self.check_answer()
                elif name == "Back":
                    return "menu"
                return
            
        # 입력창 클릭 처리
        if pygame.Rect(1025, 150, 100, 30).collidepoint(pos):
            if self.active_input != "row":
                self.row_input_backup = self.row_input or str(self.rows)
                self.row_input = ""
            self.active_input = "row"
            return "input"
        elif pygame.Rect(1025, 190, 100, 30).collidepoint(pos):
            if self.active_input != "col":
                self.col_input_backup = self.col_input or str(self.cols)
                self.col_input = ""
            self.active_input = "col"
            return "input"
        else:
            if self.active_input == "row" and not self.row_input:
                self.row_input = self.row_input_backup
            elif self.active_input == "col" and not self.col_input:
                self.col_input = self.col_input_backup
            self.active_input = None
            
        diff_rects = {
            "Easy": pygame.Rect(925, 230, 80, 30),
            "Normal": pygame.Rect(1010, 230, 80, 30),
            "Hard": pygame.Rect(1095, 230, 80, 30),
        }
        for name, rect in diff_rects.items():
            if rect.collidepoint(pos):
                self.difficulty_level = name
                return
        
        # 보드 클릭 처리
        grid_x = int((x - self.margin_left) / self.cell_size)
        grid_y = int((y - self.margin_top) / self.cell_size)
        if 0 <= grid_x < self.cols and 0 <= grid_y < self.rows:
            current = self.user_board[grid_y][grid_x]
            if button == 1:  # 좌클릭 → 칠하기/해제
                target = 0 if current != 0 else 1
            elif button == 3:  # 우클릭 → X 표시/해제
                target = 0 if current != 0 else -1
            else:
                return
            
            self.user_board[grid_y][grid_x] = target
            self.dragging = True
            self.drag_button = button
            self.drag_action = target
            self.last_drag_cell = (grid_x, grid_y)

    def handle_drag(self, pos):
        """드래그 중일 때, 마우스가 이동한 위치 처리 (한 셀당 한 번만 적용)"""
        if not self.dragging or not self.drag_button:
            return
        x, y = pos
        grid_x = int((x - self.margin_left) / self.cell_size)
        grid_y = int((y - self.margin_top) / self.cell_size)
        if not (0 <= grid_x < self.cols and 0 <= grid_y < self.rows):
            return
        if self.last_drag_cell == (grid_x, grid_y):
            return
        
        self.user_board[grid_y][grid_x] = self.drag_action
        self.last_drag_cell = (grid_x, grid_y)

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            self.draw_board()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    result = self.handle_click(event.pos, event.button)
                    if result == "menu":
                        return "menu"
                    elif result == "input":
                        continue
                    # 드래그 시작
                    self.dragging = True
                    self.drag_button = event.button
                elif event.type == pygame.MOUSEBUTTONUP:
                    # 드래그 종료
                    self.dragging = False
                    self.drag_button = None
                elif event.type == pygame.MOUSEMOTION and self.dragging:
                    # 드래그 중 마우스가 지나는 칸 처리
                    self.handle_drag(event.pos)
                elif event.type == pygame.KEYDOWN:
                    self.handle_input(event)
                
            clock.tick(30)

        pygame.quit()
        sys.exit()