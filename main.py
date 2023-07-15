import pygame
import random
import os
import sys

# 게임 설정
WIDTH = 600
HEIGHT = 600
FPS = 60

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# 게임 초기화
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invader")
clock = pygame.time.Clock()

# 이미지 로드
game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, "img")
player_img = pygame.image.load(os.path.join(img_folder, "player.png")).convert()
enemy_img = pygame.image.load(os.path.join(img_folder, "enemy.png")).convert()
bullet_img = pygame.image.load(os.path.join(img_folder, "bullet.png")).convert()

# 배경 이미지 로드
background_img = pygame.image.load(os.path.join(img_folder, "background.png")).convert()

# 점수 및 레벨 초기화
score = 0
level = 1

ranking_file = os.path.join(game_folder, "ranking.txt")

# 랭킹 정보 로드
def load_ranking():
    if not os.path.exists(ranking_file):
        return []

    ranking = []
    with open(ranking_file, "r") as file:
        for line in file:
            name, score = line.strip().split(",")
            ranking.append((name.strip(), int(score.strip())))

    return ranking

# 랭킹 정보 저장
def save_ranking(ranking):
    with open(ranking_file, "w") as file:
        for entry in ranking:
            file.write(f"{entry[0]}, {entry[1]}\n")

# 랭킹 초기화
ranking = load_ranking()

# 플레이어 클래스
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (50, 38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0

    def update(self):
        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -5
        if keystate[pygame.K_RIGHT]:
            self.speedx = 5
        self.rect.x += self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)

# 적 클래스
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(enemy_img, (50, 40))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 3)

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 10:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)

# 총알 클래스
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(bullet_img, (10, 30))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

# 모든 스프라이트 그룹
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()

# 플레이어 생성
player = Player()
all_sprites.add(player)

# 적 생성
for i in range(10):
    enemy = Enemy()
    all_sprites.add(enemy)
    enemies.add(enemy)
# 폰트 정의
font = pygame.font.Font(None, 36)

# 게임 종료 후 랭킹 출력 여부 변수
game_over = False
rank_display = False
restart = False

# 게임 루프
running = True
while running:
    # 게임 루프 (이벤트 처리)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if not game_over:
                if event.key == pygame.K_SPACE:
                    player.shoot()
                elif event.key == pygame.K_q:  # 게임 종료 안내창
                    game_over = True
            else:
                if event.key == pygame.K_r:  # 다시 시작
                    restart = True

    # 게임 루프 (게임 로직)
    if not game_over and not rank_display and not restart:
        all_sprites.update()

        # 적과 총알의 충돌 검사
        hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
        for hit in hits:
            score += 10

            enemy = Enemy()
            all_sprites.add(enemy)
            enemies.add(enemy)

        # 플레이어와 적의 충돌 검사
        hits = pygame.sprite.spritecollide(player, enemies, False)
        if hits:
            game_over = True

        # 화면 그리기
        screen.blit(background_img, (0, 0))
        all_sprites.draw(screen)

        # 실시간 점수 및 레벨 표시
        score_text = font.render(f"Score: {score}", True, WHITE)
        level_text = font.render(f"Level: {level}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (10, 50))

    if game_over and not rank_display and not restart:
        screen.fill(BLACK)
        rank_text = font.render("----- Ranking -----", True, WHITE)
        screen.blit(rank_text, (10, 10))
        ranking.append(("Player", score))
        ranking.sort(key=lambda entry: entry[1], reverse=True)
        for i, entry in enumerate(ranking[:10], 1):
            rank_entry_text = font.render(f"{i}. {entry[0]} - Score: {entry[1]}", True, WHITE)
            screen.blit(rank_entry_text, (10, 50 + i * 30))

        rank_display = True

    if restart:
        # 게임 초기화
        score = 0
        level = 1
        all_sprites.empty()
        enemies.empty()
        bullets.empty()

        # 플레이어 생성
        player = Player()
        all_sprites.add(player)

        # 적 생성
        for i in range(10):
            enemy = Enemy()
            all_sprites.add(enemy)
            enemies.add(enemy)

        game_over = False
        rank_display = False
        restart = False

    pygame.display.flip()

    # FPS 설정
    clock.tick(FPS)

pygame.quit()
sys.exit()
