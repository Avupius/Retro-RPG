import pygame 
import json

class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.spritesheet = pygame.image.load("assets/Cute_Fantasy_Free/Player/Player.png").convert_alpha()

        #Einstellungen
        self.frame_width = 32
        self.frame_height = 32
        self.frames_per_row = 6
        self.frames_scale = 1

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
        self.pos = pygame.Vector2(self.rect.topleft)
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


    def update(self, dt, collision_rect):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        moving = False
        
        if keys[pygame.K_w]:
            dy -= self.speed * dt
            self.direction = "up"
            moving = True
        if keys[pygame.K_s]:
            dy += self.speed * dt
            self.direction = "down"
            moving = True
        if keys[pygame.K_a]:
            dx -= self.speed * dt
            self.direction = "left"
            moving = True
        if keys[pygame.K_d]:
            dx += self.speed * dt
            self.direction = "right"
            moving = True
        
        #Bewegung in X/Y-Richtung und Kollision prüfung
        self.pos.x += dx
        self.rect.x = round(self.pos.x)
        for rect in collision_rect:
            if self.rect.colliderect(rect):
                self.pos.x -= dx
                self.rect.x = round(self.pos.x)
        

        self.pos.y += dy
        self.rect.y = round(self.pos.y)
        for rect in collision_rect:
            if self.rect.colliderect(rect):
                self.pos.y -= dy
                self.rect.y = round(self.pos.y)
        

        #Animationen
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

    def draw_player(self, surface, scale):
        scaled_image = pygame.transform.scale(self.image, (self.image.get_width() * scale, self.image.get_height() * scale))
        surface.blit(scaled_image, (round(self.rect.x * scale), round(self.rect.y * scale)))


class LoadMap:
    def __init__(self, map):
        with open(map) as f:
            self.map_data = json.load(f)

        self.tile_width = self.map_data["tilewidth"]
        self.tile_height = self.map_data["tileheight"]
        self.width = self.map_data["width"]
        self.height = self.map_data["height"]
        self.scale = 2
        self.interact_areas = self.load_interactions_areas()

        self.tilesets = self.load_tilesets()
        self.layers = [layer for layer in self.map_data["layers"] if layer["type"] == "tilelayer"]

    def load_tilesets(self):
        tilesets = []
        for ts in self.map_data["tilesets"]:
            image_path = ts["image"].replace("../", "")
            image = pygame.image.load(image_path).convert_alpha()
            tilesets.append({
                "firstgid": ts["firstgid"],
                "tilecount": ts["tilecount"],
                "columns": ts["columns"],
                "tilewidth": ts["tilewidth"],
                "tileheight": ts["tileheight"],
                "image": image,
                "imagewidth": ts["imagewidth"],
                "imageheight": ts["imageheight"]
            })
        print("Tilesets geladen:", [ts["firstgid"] for ts in tilesets])
        return tilesets

    def get_tile_image_by_gid(self, gid):
        if gid == 0:
            return None
        
        for ts in reversed(self.tilesets):
            if gid >= ts["firstgid"]:
                local_id = gid - ts["firstgid"]
                columns = ts["columns"]
                x = (local_id % columns) * ts["tilewidth"]
                y = (local_id // columns) * ts["tileheight"]
                rect = pygame.Rect(x, y, ts["tilewidth"], ts["tileheight"])
                if rect.right > ts["image"].get_width() or rect.bottom > ts["image"].get_height():
                    print(f"Ungültiger GID {gid} für Tileset {ts}")
                    return None  # oder ein Platzhalter-Bild
                return ts["image"].subsurface(rect)
        return None

    def draw(self, surface):
        for layer in self.layers:
            data = layer["data"]
            for i, gid in enumerate(data):
                tile = self.get_tile_image_by_gid(gid)
                if tile:
                    x = (i % self.width) * self.tile_width
                    y = (i // self.width) * self.tile_height
                    scaled_tile = pygame.transform.scale(tile, (self.tile_width * self.scale, self.tile_height * self.scale))
                    surface.blit(scaled_tile, (x * self.scale, y * self.scale))

    def get_collision_rects(self):
        rect_list = []
        for layer in self.map_data["layers"]:
            if layer["type"] == "objectgroup" and layer["name"] == "collision":
                for obj in layer["objects"]:
                    x = obj["x"]
                    y = obj["y"]
                    w = obj["width"]
                    h = obj["height"]
                    rect_list.append(pygame.Rect(x, y, w, h))
        return rect_list

    def load_interactions_areas(self):
        areas = []
        for layer in self.map_data["layers"]:
            if layer["type"] == "objectgroup" and layer["name"] == "interact":
                for obj in layer["objects"]:
                    rect = pygame.Rect(obj["x"], obj["y"], obj["width"], obj["height"])
                    props = {p["name"]: p["value"] for p in obj.get("properties", [])}
                    areas.append((rect, props))
        return areas


# -- Game-Loop Funktionen --
def check_interactions(player, current_map):
    for area, props in current_map.interact_areas:
        if player.rect.colliderect(area):
            if "target_map" in props:
                new_map = LoadMap(f"maps/{props['target_map']}")
                spawn_x = props.get("spawn_x", 100)
                spawn_y = props.get("spawn_y", 100)
                player.pos = pygame.Vector2(spawn_x, spawn_y)
                player.rect.topleft = player.pos
                return new_map
    return current_map


# -- Spiel Setup --
pygame.init()
screen_scale = 2
screen_x = 640 * screen_scale
screen_y = 480 * screen_scale
screen = pygame.display.set_mode((screen_x, screen_y))
clock = pygame.time.Clock()
running = True
dt = 0
game_map = LoadMap("maps/Map_home.json")

# -- Player erstellen --
player = Player((100,80))

# -- Game Loop--
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    screen.fill((0, 0, 0))

    # Player movment & Kollsion
    collision_rects = game_map.get_collision_rects()
    player.update(dt, collision_rects)
    
    game_map = check_interactions(player, game_map)

    # Bildshirm zeichen
    game_map.draw(screen)
    player.draw_player(screen,scale=screen_scale)
    pygame.display.flip()

    # Frames Berechnung
    dt = clock.tick(60) / 1000


pygame.quit()
