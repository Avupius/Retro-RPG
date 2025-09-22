import pygame
from attackhitbox import AttackHitbox


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, attack_sprites = None, enemies_group = None):
        super().__init__()
        self.spritesheet = pygame.image.load("assets/Cute_Fantasy_Free/Player/Player.png").convert_alpha()

        #Einstellungen
        self.frame_width = 32
        self.frame_height = 32
        self.frames_per_row = 6

        #Schwert Schwung Sound
        self.sword_swing = pygame.mixer.Sound("assets/sword.wav")
        self.sword_swing.set_volume(0.5)

        #Move-Frames
        self.frames = {
            "down": self.load_frames(3),
            "up": self.load_frames(2),
            "right": self.load_frames(1),
            "down": self.load_frames(3),
            "left": [pygame.transform.flip(f,True, False) for f in self.load_frames(1)]
            }

        #Startwerte
        self.direction = "down"
        self.frame_index = 0
        self.animation_timer = 0
        self.image = self.frames[self.direction][self.frame_index]
        self.rect = self.image.get_rect(topleft = pos)
        self.pos = pygame.Vector2(self.rect.topleft)
        self.speed = 100

        #Playerwerte
        self.max_hp = 100
        self.hp = self.max_hp
        self.invu_ms = 700
        self.hurt_until = 0

        #Angrifswerte
        self.attack_damage = 10
        self.attack_range = 28
        self.attack_width = 14
        self.attack_duration = 120
        self.attack_cooldown = 350
        self.last_attack_time = -1_000_000

        #Angrifsprites 
        self.attack_frames = {
            "right": self.load_frames(7,count=4),
            "down": self.load_frames(6,count=4),
            "up": self.load_frames(8,count=4),
            "left": [pygame.transform.flip(f, True, False) for f in self.load_frames(7,count=4)]
        }

        self.mode = "idle"
        self.attack_timer = 0.0
        self.attack_frame_index = 0
        self.attack_dir_on_start = "down"
        self.attack_anim_speed = 0.1

        #Referenzen auf Gruppen
        self.attack_sprites = attack_sprites
        self.enemies_group = enemies_group
    
    #Frames aus Spreadsheet laden
    def load_frames(self, row, count: int | None = None):
        frames = []
        sheet_cols = self.spritesheet.get_width() // self.frame_width
        n = count if count is not None else min(self.frames_per_row, sheet_cols)
        for i in range(n):
            x = i * self.frame_width
            y = row * self.frame_height
            frame = self.spritesheet.subsurface(pygame.Rect(x, y, self.frame_width, self.frame_height))
            frames.append(frame)
        return frames

    def update(self, dt, collision_rect):
        keys = pygame.key.get_pressed()
        if self.mode != "attack":
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
                self.mode = "move"
                    
            else:
                #Stillstand erstes Frame
                self.frame_index = 0
                self.image = self.frames[self.direction][self.frame_index]
                self.mode = "idle"
            
            if keys[pygame.K_SPACE]:
                self.attack()
        else:
            self.attack_timer += dt
            if self.attack_timer >= self.attack_anim_speed:
                self.attack_timer -= self.attack_anim_speed
                self.attack_frame_index += 1
                if self.attack_frame_index >= len(self.attack_frames[self.attack_dir_on_start]):
                    self.mode = "idle"
                    self.attack_frame_index = 0

            self.image = self.attack_frames[self.attack_dir_on_start][self.attack_frame_index]

            if self.attack_frame_index == 1:
                self.spawn_attack_hitbox(direction_override=self.attack_dir_on_start)


    def draw_player(self, surface, scale):
        scaled_image = pygame.transform.scale(self.image, (self.image.get_width() * scale, self.image.get_height() * scale))
        surface.blit(scaled_image, (round(self.rect.x * scale), round(self.rect.y * scale)))

        #Player HP HUD
        hud_w = 140
        hud_h = 12
        ratio = self.hp / self.max_hp
        pygame.draw.rect(surface, (40 ,40 ,40), (12, 12, hud_w, hud_h))
        pygame.draw.rect(surface, (40, 180, 40), (12, 12, int(hud_w * ratio), hud_h))
        pygame.draw.rect(surface, (0, 0, 0), (12, 12, hud_w, hud_h), 1)


    def attack(self):
        if self.attack_sprites is None or self.enemies_group is None:
            return
        now = pygame.time.get_ticks()
        if now - self.last_attack_time < self.attack_cooldown:
            return

        self.last_attack_time = now
        self.mode = "attack"
        self.attack_timer = 0.0
        self.attack_frame_index = 0
        self.attack_dir_on_start = self.direction

        self.sword_swing.play()
    
    #Hitbox für Angriffe
    def spawn_attack_hitbox(self, direction_override=None):
        direction = direction_override or self.direction
        hitbox = AttackHitbox(
            owner = self,
            damage = self.attack_damage,
            range_px = self.attack_range,
            width_px = self.attack_width,
            duration_ms = self.attack_duration,
            direction = direction,
            enemies_group = self.enemies_group
        )
        self.attack_sprites.add(hitbox)

    def take_damage(self, amount):
        now = pygame.time.get_ticks()
        if now < self.hurt_until:
            return

        self.hp = max(0, self.hp - amount)
        self.hurt_until = now + self.invu_ms

        if self.hp == 0:
            print("Player Down") #TODO Respawn