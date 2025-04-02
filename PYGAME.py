import pygame
import random

# Configuración de la pantalla
WIDTH = 800
HEIGHT = 600
FPS = 60

# Inicialización de Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Juego de disparos")

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Intentar cargar el fondo de espacio
try:
    space_background = pygame.image.load("space_background.jpg")
    space_background = pygame.transform.scale(space_background, (WIDTH, HEIGHT))
except FileNotFoundError:
    # Si no se encuentra la imagen, usar un fondo negro
    space_background = pygame.Surface((WIDTH, HEIGHT))
    space_background.fill(BLACK)

# Clase base
class Entity:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image

    def move(self):
        pass

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

# Clase Character que hereda de Entity
class Character(Entity):
    def __init__(self, x, y, image, lives):
        super().__init__(x, y, image)
        self.lives = lives
        self.is_alive = True

    def collide(self, other):
        if self.x < other.x + other.image.get_width() and self.x + self.image.get_width() > other.x:
            if self.y < other.y + other.image.get_height() and self.y + self.image.get_height() > other.y:
                return True
        return False

# Clase Player que hereda de Character
class Player(Character):
    def __init__(self, x, y, image):
        super().__init__(x, y, image, lives=3)
        self.score = 0

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= 5
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.image.get_width():
            self.x += 5
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= 5
        if keys[pygame.K_DOWN] and self.y < HEIGHT - self.image.get_height():
            self.y += 5

    def shoot(self):
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            return Shot(self.x + self.image.get_width() // 2, self.y)
        return None

# Clase Opponent que hereda de Character
class Opponent(Character):
    def __init__(self, x, y, image):
        super().__init__(x, y, image, lives=1)

    def move(self):
        self.y += 3

# Clase Shot que hereda de Entity
class Shot(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, pygame.Surface((5, 10)))
        self.image.fill(WHITE)

    def move(self):
        self.y -= 5

    def hit_target(self):
        return self.y < 0

    def collide(self, other):
        # Comprobar si el disparo colisiona con otro objeto
        if (self.x < other.x + other.image.get_width() and
            self.x + self.image.get_width() > other.x and
            self.y < other.y + other.image.get_height() and
            self.y + self.image.get_height() > other.y):
            return True
        return False

# Clase Game
class Game:
    def __init__(self):
        self.is_running = True
        self.score = 0
        self.player = Player(WIDTH // 2, HEIGHT - 60, pygame.Surface((50, 50)))
        self.player.image.fill((0, 255, 0))
        self.opponents = []
        self.shots = []
        self.enemy_spawn_time = 30
        self.enemy_spawn_counter = 0
        self.player_lives = 3

    def spawn_enemy(self):
        enemy = Opponent(random.randint(0, WIDTH - 50), 0, pygame.Surface((50, 50)))
        enemy.image.fill((255, 0, 0))
        self.opponents.append(enemy)

    def update(self):
        self.enemy_spawn_counter += 1
        if self.enemy_spawn_counter >= self.enemy_spawn_time:
            self.spawn_enemy()
            self.enemy_spawn_counter = 0

        self.player.move()
        shot = self.player.shoot()
        if shot:
            self.shots.append(shot)

        for shot in self.shots:
            shot.move()

        for opponent in self.opponents:
            opponent.move()

        self.check_collisions()
        self.remove_dead_entities()

        if self.player_lives <= 0:
            self.end_game("GAME OVER")
        if self.score >= 100:
            self.end_game("YOU WIN")

    def check_collisions(self):
        for shot in self.shots:
            for opponent in self.opponents:
                if shot.collide(opponent):
                    self.score += 1
                    self.shots.remove(shot)
                    self.opponents.remove(opponent)
                    break

        for opponent in self.opponents:
            if opponent.collide(self.player):
                self.player_lives -= 1
                self.opponents.remove(opponent)

    def remove_dead_entities(self):
        self.shots = [shot for shot in self.shots if not shot.hit_target()]
        self.opponents = [opponent for opponent in self.opponents if opponent.y < HEIGHT]

    def end_game(self, message):
        self.is_running = False
        font = pygame.font.SysFont(None, 72)
        text = font.render(message, True, WHITE)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
        pygame.display.flip()
        pygame.time.wait(3000)
        self.ask_restart()

    def ask_restart(self):
        font = pygame.font.SysFont(None, 36)
        text = font.render("¿Quieres jugar de nuevo? (S/N)", True, WHITE)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + 50))
        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        self.__init__()
                        waiting = False
                    elif event.key == pygame.K_n:
                        pygame.quit()
                        exit()

    def draw(self):
        screen.blit(space_background, (0, 0))
        self.player.draw(screen)
        for opponent in self.opponents:
            opponent.draw(screen)
        for shot in self.shots:
            shot.draw(screen)

        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        lives_text = font.render(f"Lives: {self.player_lives}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (WIDTH - 150, 10))

        pygame.display.flip()

def main():
    clock = pygame.time.Clock()
    game = Game()

    while game.is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.is_running = False

        game.update()
        game.draw()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()