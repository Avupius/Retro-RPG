import pygame 

class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((32,48))
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect(topleft=pos)
        self.speed = 5

    def player_movment(self, dt):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_w]:
            self.rect.y -= 300 * dt
        if keys[pygame.K_s]:
            self.rect.y += 300 * dt
        if keys[pygame.K_a]:
            self.rect.x -= 300 * dt
        if keys[pygame.K_d]:
            self.rect.x += 300 * dt




# -- Spiel Setup --
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0


# -- Player erstellen --
player = Player((100,100))
all_sprites = pygame.sprite.Group(player)



# -- Game Loop--
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Player movment
    player.player_movment(dt)

    # Bildshirm zeichen
    screen.fill("purple")
    all_sprites.draw(screen)
    pygame.display.flip()

    # Frames erechnung
    dt = clock.tick(60) / 1000


pygame.quit()
