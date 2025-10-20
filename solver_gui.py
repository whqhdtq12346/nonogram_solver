import pygame
import sys
import os
import threading
import tkinter as tk
from tkinter import filedialog
from solver import NonogramSolver

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


class InputBox:
    def __init__(self, x, y, w, h, font, ori='horizontal'):
        self.rect = pygame.Rect(0, 0, w, h)
        self.rect.center = (x, y)
        self.color = DARK_GRAY
        self.active = False
        self.text = ''
        self.font = font
        self.txt_surface = self.font.render(self.text, True, BLACK)
        self.ori = ori

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = BLUE if self.active else DARK_GRAY
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.text += '\n'
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_SPACE and self.ori == 'vertical':
                # 세로 힌트는 스페이스바 → 줄바꿈
                self.text += '\n'
            else:
                self.text += event.unicode
            self.txt_surface = self.font.render(self.text, True, BLACK)

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect)
        pygame.draw.rect(screen, self.color, self.rect, 2)
        if self.ori == 'horizontal':
            # 오른쪽 정렬
            text_surface = self.font.render(self.text, True, BLACK)
            text_rect = text_surface.get_rect()
            text_rect.right = self.rect.right - 5
            text_rect.centery = self.rect.centery
            screen.blit(text_surface, text_rect)
        else:
            # 세로 힌트
            y = self.rect.top + 5
            for line in self.text.split('\n'):
                text_surface = self.font.render(line, True, BLACK)
                text_rect = text_surface.get_rect(centerx=self.rect.centerx)
                text_rect.y = y
                screen.blit(text_surface, text_rect)
                y += self.font.get_height() + 2

    def get_value(self):
        return self.text.strip()



class SolverGUI:
    def __init__(self):
        # 기본 설정
        self.rows = 5
        self.cols = 5
        self.row_hint = [[] for _ in range(self.rows)]
        self.col_hint = [[] for _ in range(self.cols)]
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.difficulty_value = None
        self.file_path_holder = {"path": None}
        
        # GUI
        self.margin_left = 150
        self.margin_top = 150
        self.cell_size = 30

        # input
        self.active_input = None
        self.row_input = ""
        self.col_input = ""
        self.row_hint_boxes = []
        self.col_hint_boxes = []

        # 메시지
        self.message = ""
        self.message_timer = 0

        # 타이머
        self.start_time = None
        self.elapsed_time = 0
        self.timer_running = False
        
        self.update_board(self.rows, self.cols)
        self.screen = pygame.display.set_mode((1200, 900))
        pygame.display.set_caption("Nonogram Solver")

        # 버튼 정의
        self.buttons = {
            "Load": pygame.Rect(975, 250, 150, 40),
            "Solve": pygame.Rect(975, 300, 150, 40),
            "Reset": pygame.Rect(975, 350, 150, 40),
            "Back": pygame.Rect(975, 400, 150, 40),
        }

        self.solver = NonogramSolver()
        
    def update_board(self, rows, cols):
        """row, col 변경 시 보드와 힌트 초기화"""
        self.rows = rows
        self.cols = cols
        self.row_hint = [[] for _ in range(rows)]
        self.col_hint = [[] for _ in range(cols)]
        self.board = [[0 for _ in range(cols)] for _ in range(rows)]
        self.cell_size = min(30, int(720 / max(rows, cols)))
        
        self.row_hint_boxes = []
        self.col_hint_boxes = []
        
        font_hint = pygame.font.Font("font/NanumGothic.otf", int(self.cell_size * 0.6))
        
        # 행 힌트 입력창 생성 (왼쪽)
        for i in range(rows):
            x = 75
            y = self.margin_top + (i + 0.5) * self.cell_size
            box = InputBox(x, y, 140, 0.9 * self.cell_size, font_hint, ori='horizontal')
            self.row_hint_boxes.append(box)

        # 열 힌트 입력창 생성 (위쪽)
        for j in range(cols):
            x = self.margin_left + (j + 0.5) * self.cell_size
            y = 75
            box = InputBox(x, y, 0.9 * self.cell_size, 140, font_hint, ori='vertical')
            self.col_hint_boxes.append(box)

    def draw_inputs(self):
        # 힌트 입력창
        for box in self.row_hint_boxes + self.col_hint_boxes:
            box.draw(self.screen)
        
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

        text_r = font_18.render(self.row_input or str(self.rows), True, BLACK)
        text_c = font_18.render(self.col_input or str(self.cols), True, BLACK)
        self.screen.blit(text_r, (row_box.x + 10, row_box.y + 5))
        self.screen.blit(text_c, (col_box.x + 10, col_box.y + 5))

    def draw_board(self):
        self.screen.fill(WHITE)
        self.draw_inputs()
        self.cell_size = min(30, int(720 / max(self.rows, self.cols)))

        # 보드 그리기
        for r in range(self.rows):
            for c in range(self.cols):
                x = self.margin_left + c * self.cell_size
                y = self.margin_top + r * self.cell_size
                rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                val = self.board[r][c]
                color = WHITE
                if val == 1:
                    color = DARK_GRAY
                elif val == -1:
                    color = GRAY
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, DARK_GRAY, rect, 1)

        # 5칸마다 굵은 선
        board_width = self.cols * self.cell_size
        board_height = self.rows * self.cell_size
        for i in range(self.rows + 1):
            y = self.margin_top + i * self.cell_size
            width = 3 if i % 5 == 0 else 1
            pygame.draw.line(self.screen, BLACK, (self.margin_left, y), (self.margin_left + board_width, y), width)
        for j in range(self.cols + 1):
            x = self.margin_left + j * self.cell_size
            width = 3 if j % 5 == 0 else 1
            pygame.draw.line(self.screen, BLACK, (x, self.margin_top), (x, self.margin_top + board_height), width)

        # 타이머
        if self.start_time is not None and self.timer_running:
            self.elapsed_time = pygame.time.get_ticks() - self.start_time
        elif self.start_time is not None and not self.timer_running:
            pass
        minutes = self.elapsed_time // 60000
        seconds = (self.elapsed_time // 1000) % 60
        ms = self.elapsed_time % 1000
        time_str = f"{minutes:02}:{seconds:02}:{ms:03}"
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
            msg_surface = font_22.render(self.message, True, (0, 128, 0) if self.message == "Solved!" else (200, 0, 0))
            msg_rect = msg_surface.get_rect(center=(1050, 600))
            self.screen.blit(msg_surface, msg_rect)
            
        pygame.display.flip()
        
    def load_puzzle(self):
        """파일 탐색기에서 .txt 파일 선택 후 퍼즐을 가져온다"""
        pygame.display.iconify()
        
        file_path_holder = self.file_path_holder
        def select_file():
            root = tk.Tk()
            root.withdraw()
            
            path = filedialog.askopenfilename(
                title="Select the puzzle file.",
                filetypes=[("Text Files", "*.txt")],
                initialdir=os.getcwd()
            )
            root.destroy()
            if path: file_path_holder["path"] = path
        
        t = threading.Thread(target=select_file, daemon=True)
        t.start()
        pygame.display.set_mode((1200, 900))
        
    def apply_file(self):
        file_path = self.file_path_holder["path"]
        print(file_path)
        
        if not file_path:
            self.message = "File not selected."
            self.message_timer = pygame.time.get_ticks()
            return

        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        row_hint = []
        col_hint = []

        row = False
        for line in lines:
            line = line.strip()
            if line.startswith("Row:"):
                row = True
                continue
            elif line.startswith("Col:"):
                row = False
                continue
            else:
                hint = list(line.split(' '))
                if row: row_hint.append(hint)
                else: col_hint.append(hint)
        
        self.update_board(len(row_hint), len(col_hint))
        # 힌트 GUI에 반영
        for i, hint in enumerate(row_hint):
            if i < len(self.row_hint_boxes):
                self.row_hint_boxes[i].text = ' '.join(hint)
                self.row_hint_boxes[i].txt_surface = self.row_hint_boxes[i].font.render(self.row_hint_boxes[i].text, True, BLACK)
        for j, hint in enumerate(col_hint):
            if j < len(self.col_hint_boxes):
                self.col_hint_boxes[j].text = '\n'.join(hint)
                self.col_hint_boxes[j].txt_surface = self.col_hint_boxes[j].font.render(hint[0], True, BLACK)
        
        self.message = f"Puzzle ({len(row_hint)}x{len(col_hint)}) loaded."
        self.message_timer = pygame.time.get_ticks()
        
    def solve_puzzle(self):
        """Solve 버튼 클릭 시 hint를 가져오고 새로운 thread에서 Solver 실행"""
        def solver_thread():
            def parse_hint(text):
                text = text.strip()
                if not text: return [0]
                return [int(x) for x in text.split() if x.isdigit()]

            # 힌트 parsing
            self.row_hint = [parse_hint(b.get_value()) for b in self.row_hint_boxes]
            self.col_hint = [parse_hint(b.get_value()) for b in self.col_hint_boxes]
            
            # 타이머 시작
            self.start_time = pygame.time.get_ticks()
            self.elapsed_time = 0
            self.timer_running = True

            # Solver 호출
            self.solver.set_problem(self.row_hint, self.col_hint)
            if self.solver.solve_problem(log=False):
                self.message = "Solved!"
                self.difficulty_value = self.solver.difficulty
            else:
                self.message = "Cannot solve the problem."
                
            self.message_timer = pygame.time.get_ticks()
            self.board = self.solver.board
            self.timer_running = False
        
        threading.Thread(target=solver_thread, daemon=True).start()

    def handle_input(self, event):
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
                    
            # 숫자가 입력될 때마다 업데이트
            try:
                new_r = int(self.row_input or self.rows)
                new_c = int(self.col_input or self.cols)
                if new_r > 50 or new_c > 50:
                    return
                self.update_board(new_r, new_c)
            except ValueError:
                pass

    def handle_click(self, pos, button):
        # 버튼 클릭
        for name, rect in self.buttons.items():
            if rect.collidepoint(pos):
                if name == "Load":
                    self.load_puzzle()
                elif name == "Solve":
                    self.solve_puzzle()
                elif name == "Reset":
                    self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
                elif name == "Back":
                    return "menu"

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

    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            self.draw_board()
            if self.file_path_holder["path"]:
                self.apply_file()
                self.file_path_holder["path"] = None
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    result = self.handle_click(event.pos, event.button)
                    if result == "menu":
                        return "menu"
                elif event.type == pygame.KEYDOWN:
                    self.handle_input(event)
                for box in self.row_hint_boxes + self.col_hint_boxes:
                    box.handle_event(event)

            clock.tick(30)
            
        pygame.quit()
        sys.exit()
        