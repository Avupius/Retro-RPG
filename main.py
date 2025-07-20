import pygame 

class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.spritesheet = pygame.image.load("assets/Player.png").convert_alpha()

        #Einstellungen
        self.frame_width = 32
        self.frame_height = 32
        self.frames_per_row = 6
        self.frames_scale = 2

        #Frames vorbereiten
        self.frames = {
            "down": self.load_frames(0),
            "left": self.load_frames(3),
            "right": self.load_frames(1),
            "up" : self.load_frames(2)
        }

        #Start
        self.direction = "down"
        self.frame_index = 0
        self.animation_timer = 0
        self.image = self.frames[self.direction][self.frame_index]
        self.rect = self.image.get_rect(topleft = pos)
        self.speed = 100

    def load_frames(self, row):
        frames = []
        for i in range(self.frames_per_row):
            frame = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
            x = i * self.frame_width
            y = row * self.frame_height
            frame.blit(self.spritesheet, (0, 0), pygame.Rect(x, y, self.frame_width, self.frame_height))
            frame = pygame.transform.scale(frame, (self.frame_width * self.frames_scale, self.frame_height * self.frames_scale))
            frames.append(frame)
        return frames


    def update(self, dt):
        keys = pygame.key.get_pressed()
        moving = False
        
        if keys[pygame.K_w]:
            self.rect.y -= self.speed * dt
            self.direction = "up"
            moving = True
        if keys[pygame.K_s]:
            self.rect.y += self.speed * dt
            self.direction = "down"
            moving = True
        if keys[pygame.K_a]:
            self.rect.x -= self.speed * dt
            self.direction = "left"
            moving = True
        if keys[pygame.K_d]:
            self.rect.x += self.speed * dt
            self.direction = "right"
            moving = True

        if moving:
            self.animation_timer += dt
            if self.animation_timer >= 0.1:
                self.animation_timer = 0
                self.frame_index = (self.frame_index + 1) % self.frames_per_row
                self.image = self.frames[self.direction][self.frame_index]
                
        else:
            #Stillstand erstes Frame
            self.frame_index = 0
            self.image = self.frames[self.direction][self.frame_index]


# -- Spiel Setup --
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0


# -- Player erstellen --
player = Player((100,100))
all_sprites = pygame.sprite.Group(player)

# -- Map - Layout --
tile_size = 32

# Bestehende Tiles laden und skalieren
grass_tile = pygame.transform.scale( 
        pygame.image.load("assets/Grass_Middle.png").convert_alpha(),
        (tile_size, tile_size)
    )

path_tile = pygame.transform.scale(
        pygame.image.load("assets/Path_Middle.png").convert_alpha(),
        (tile_size, tile_size)
    )

water_tile = pygame.transform.scale(
        pygame.image.load("assets/Water_Middle.png").convert_alpha(),
        (tile_size, tile_size)
    )

# -- Weg-Tileset laden und aufteilen --
path_tileset = pygame.image.load("assets/Path_Tile.png").convert_alpha()
original_tile_size = 16  # falls dein Tileset 16x16 Tiles hat

def get_tile(tileset ,x, y):
    tile = pygame.Surface((original_tile_size, original_tile_size), pygame.SRCALPHA)
    tile.blit(tileset, (0, 0), pygame.Rect(x * original_tile_size, y * original_tile_size, original_tile_size, original_tile_size))
    tile = pygame.transform.scale(tile, (tile_size, tile_size))  # skalieren auf 256x256
    return tile

# Weg-Tiles extrahieren
weg_rand  = get_tile(path_tileset, 0, 0)
weg_mitte = get_tile(path_tileset, 1, 0)
weg_ecke  = get_tile(path_tileset, 0, 1)
fuss_spur = get_tile(path_tileset, 0, 2)

# -- Tile-Images definieren --
tile_images = {
    0: grass_tile,
    1: path_tile,
    2: water_tile,
    3: weg_mitte,
    4: weg_rand,
    5: weg_ecke,
    6: fuss_spur
}

# -- Map-Layout erweitern --
map_layout = [
    [0, 1, 3, 3, 2],
    [4, 3, 6, 3, 2],
    [5, 0, 0, 3, 2],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 4, 3, 4, 0],
    [0, 4, 3, 4, 0],
]


# -- Game Loop--
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    screen.fill((0, 0, 0))

    # Player movment
    player.update(dt)

    # Bildshirm zeichen
    for row_index, row in enumerate(map_layout):
        for col_index, tile_id in enumerate(row):
            tile_surface = tile_images[tile_id]
            x = col_index * tile_size
            y = row_index * tile_size
            screen.blit(tile_surface, (x, y))


    all_sprites.draw(screen)
    pygame.display.flip()

    # Frames erechnung
    dt = clock.tick(60) / 1000


pygame.quit()
