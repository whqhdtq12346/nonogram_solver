import pygame
import sys
from generator import NonogramGenerator
from solver import NonogramSolver
from generator_gui import GeneratorGUI
from solver_gui import SolverGUI

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



# ================================================================
# 메인 GUI 클래스
# ================================================================
class NonogramApp:
    def __init__(self):
        self.mode = "menu"  # "menu", "generator", "solver"
        self.gui = None
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Nonogram")

    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            if self.mode == "menu":
                running = self.show_main_menu()
            elif self.mode == "generator":
                running = self.run_generator_mode()
            elif self.mode == "solver":
                running = self.run_solver_mode()
            clock.tick(30)
        pygame.quit()
        sys.exit()

    # =============================================================
    # 메인 메뉴 화면
    # =============================================================
    def show_main_menu(self):
        self.screen.fill(WHITE)
        scr_width, scr_height = self.screen.get_size()
        
        title = font_36.render("Nonogram", True, BLACK)
        self.screen.blit(title, (scr_width // 2 - title.get_width() // 2, 150))

        # 버튼 정의
        buttons = {
            "Generator": pygame.Rect(scr_width // 2 - BUTTON_WIDTH // 2, 250, BUTTON_WIDTH, BUTTON_HEIGHT),
            "Solver": pygame.Rect(scr_width // 2 - BUTTON_WIDTH // 2, 310, BUTTON_WIDTH, BUTTON_HEIGHT),
            "Quit": pygame.Rect(scr_width // 2 - BUTTON_WIDTH // 2, 370, BUTTON_WIDTH, BUTTON_HEIGHT),
        }

        for name, rect in buttons.items():
            pygame.draw.rect(self.screen, BLUE, rect)
            pygame.draw.rect(self.screen, BLACK, rect, 2)
            text = font_18.render(name, True, BLACK)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for name, rect in buttons.items():
                    if rect.collidepoint(event.pos):
                        if name == "Generator":
                            self.mode = "generator"
                            self.gui = GeneratorGUI()
                            return True
                        elif name == "Solver":
                            self.mode = "solver"
                            return True
                        elif name == "Quit":
                            return False
        return True

    # Generator Mode 실행
    def run_generator_mode(self):
        if self.gui is None:
            self.gui = GeneratorGUI()
        result = self.gui.run()
        if result == "menu":
            self.mode = "menu"
            self.gui = None
            self.screen = pygame.display.set_mode((800, 600))
        return True

    # Solver Mode 실행 (지금은 더미)
    def run_solver_mode(self):
        if self.gui is None:
            self.gui = SolverGUI()
        result = self.gui.run()
        if result == "menu":
            self.mode = "menu"
            self.gui = None
            self.screen = pygame.display.set_mode((800, 600))
        return True

# 실행
if __name__ == "__main__":
    app = NonogramApp()
    app.run()
