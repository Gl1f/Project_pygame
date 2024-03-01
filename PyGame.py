import pygame
import sys
import random

pygame.init()

# Определение констант для экрана
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BROWN = (205, 133, 63)  # Нежно-коричневый цвет

# Параметры лабиринта
LINE_WIDTH = 10
LINE_GAP = 40
LINE_OFFSET = 20
DOOR_WIDTH = 20
DOOR_GAP = 40
MAX_OPENINGS_PER_LINE = 5

# Параметры и начальная позиция игрока
PLAYER_RADIUS = 10
PLAYER_SPEED = 0.05
PLAYER_X = WIDTH - 12
PLAYER_Y = HEIGHT - LINE_OFFSET


# Функция создания лабиринта
def create_maze():
    lines = []
    for i in range(0, WIDTH, LINE_GAP):
        rect = pygame.Rect(i, 0, LINE_WIDTH, HEIGHT)
        num_openings = random.randint(1, MAX_OPENINGS_PER_LINE)
        if num_openings == 1:
            door_pos = random.randint(LINE_OFFSET + DOOR_WIDTH, HEIGHT - LINE_OFFSET - DOOR_WIDTH)
            lines.append(pygame.Rect(i, 0, LINE_WIDTH, door_pos - DOOR_WIDTH))
            lines.append(pygame.Rect(i, door_pos + DOOR_WIDTH, LINE_WIDTH, HEIGHT - door_pos - DOOR_WIDTH))
        else:
            opening_positions = [0] + sorted([random.randint(LINE_OFFSET + DOOR_WIDTH,
                                                             HEIGHT - LINE_OFFSET - DOOR_WIDTH)
                                              for _ in range(num_openings - 1)]) + [HEIGHT]
            for j in range(num_openings):
                lines.append(pygame.Rect(i, opening_positions[j],
                                         LINE_WIDTH, opening_positions[j + 1] - opening_positions[j] - DOOR_WIDTH))
    return lines


# Класс игры
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.HWSURFACE
                                              | pygame.DOUBLEBUF | pygame.FULLSCREEN)
        pygame.display.set_caption("Лабиринт")
        self.clock = pygame.time.Clock()
        self.running = True
        self.playing = False
        self.maze_lines = []
        self.player_x = PLAYER_X
        self.player_y = PLAYER_Y

    def new(self):
        self.playing = True
        self.maze_lines = create_maze()
        self.run()

    def run(self):
        while self.playing:
            self.events()
            self.update()
            self.draw()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.playing = False
                elif event.key == pygame.K_SPACE:
                    self.maze_lines = create_maze()  # Перегенерация лабиринта при нажатии пробела

    # В методе update класса Game проверяем, достиг ли игрок нижней стены или левой стены
    def update(self):
        # Генерация лабиринта раз в секунду
        if pygame.time.get_ticks() % 1000 == 0:
            self.maze_lines = create_maze()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.player_x > PLAYER_RADIUS:
            self.player_x -= PLAYER_SPEED
        elif keys[pygame.K_RIGHT] and self.player_x < WIDTH - PLAYER_RADIUS:
            self.player_x += PLAYER_SPEED
        elif keys[pygame.K_UP] and self.player_y > PLAYER_RADIUS:
            self.player_y -= PLAYER_SPEED
        elif keys[pygame.K_DOWN] and self.player_y < HEIGHT - PLAYER_RADIUS:
            self.player_y += PLAYER_SPEED

        # Проверяем, достиг ли игрок левой стены за пределами лабиринта
        if self.player_x <= 10:
            self.show_congratulations_window("Мои поздравления, вы выиграли!")

        # Проверяем, достиг ли игрок нижней стены за пределами лабиринта
        if self.player_y >= HEIGHT - 10:
            self.show_congratulations_window("Касаться пола нельзя, вы проиграли!")

        player_rect = pygame.Rect(self.player_x - PLAYER_RADIUS, self.player_y - PLAYER_RADIUS, PLAYER_RADIUS * 2,
                                  PLAYER_RADIUS * 2)
        for line in self.maze_lines:
            if line.colliderect(player_rect):
                if self.player_x > line.left and self.player_x < line.right:
                    if self.player_y < line.top:
                        self.player_y = line.top - PLAYER_RADIUS
                    else:
                        self.player_y = line.bottom + PLAYER_RADIUS
                elif self.player_y > line.top and self.player_y < line.bottom:
                    if self.player_x < line.left:
                        self.player_x = line.left - PLAYER_RADIUS
                    else:
                        self.player_x = line.right + PLAYER_RADIUS

    # Метод для отображения окна с сообщением
    def show_congratulations_window(self, message):
        # Блокируем игровой процесс
        self.playing = False

        # Отрисовываем сообщение
        font = pygame.font.Font(None, 48)
        text = font.render(message, True, WHITE)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(text, text_rect)

        # Отрисовываем кнопку
        button_font = pygame.font.Font(None, 36)
        back_text = button_font.render("Вернуться в меню", True, WHITE)
        back_rect = back_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        pygame.draw.rect(self.screen, BROWN, back_rect)
        self.screen.blit(back_text, back_rect.topleft)

        pygame.display.flip()

        # Ожидаем нажатия клавиши для возврата в меню
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        waiting = False
                        self.return_to_menu()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if back_rect.collidepoint(event.pos):
                        waiting = False
                        self.return_to_menu()

    # Метод для возврата в главное меню
    def return_to_menu(self):
        self.running = False
        menu = MainMenu()
        menu.run()

    def draw(self):
        self.screen.fill(BLACK)
        for line in self.maze_lines:
            pygame.draw.rect(self.screen, GREEN, line)
        pygame.draw.circle(self.screen, RED, (self.player_x, self.player_y), PLAYER_RADIUS)
        pygame.display.flip()

    def toggle_fullscreen(self):
        pygame.display.toggle_fullscreen()


# Класс главного меню
class MainMenu:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.HWSURFACE
                                              | pygame.DOUBLEBUF | pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.Font(None, 48)
        self.button_font = pygame.font.Font(None, 36)
        self.title_text = self.font.render("Лабиринт", True, BROWN)
        self.start_button = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 50, 300, 50)
        self.exit_button = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 50, 300, 50)
        self.start_text = self.button_font.render("Начать новую иигру!", True, BLACK)
        self.exit_text = self.button_font.render("Выйти из игры", True, BLACK)

    def run(self):
        while self.running:
            self.events()
            self.draw()
            self.clock.tick(FPS)

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    if self.start_button.collidepoint(mouse_pos):
                        self.running = False
                        game = Game()
                        game.new()
                    elif self.exit_button.collidepoint(mouse_pos):
                        pygame.quit()
                        sys.exit()

    def draw(self):
        # Загрузка фонового изображения и его растягивание на весь экран
        background = pygame.image.load("background.jpg").convert()
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
        self.screen.blit(background, (0, 0))

        # Отрисовка названия игры
        self.screen.blit(self.title_text, (WIDTH // 2 - self.title_text.get_width() // 2, 50))

        # Отрисовка кнопок
        pygame.draw.rect(self.screen, BROWN, self.start_button)
        pygame.draw.rect(self.screen, BROWN, self.exit_button)
        self.screen.blit(self.start_text, (WIDTH // 2 - self.start_text.get_width() // 2, HEIGHT // 2 - 25))
        self.screen.blit(self.exit_text, (WIDTH // 2 - self.exit_text.get_width() // 2, HEIGHT // 2 + 75))

        pygame.display.flip()


def main():
    menu = MainMenu()
    menu.run()


if __name__ == "__main__":
    main()
