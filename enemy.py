import pygame



class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, quest_giver,spritesheet_path, frame_width=32, frame_height=32, frames_per_row=3, speed=1, movebox_inset: tuple[int, int] | None = None):
        super().__init__()
        self.spritesheet = pygame.image.load(spritesheet_path).convert_alpha()
        
        #Pixel Einstellungen
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.frames_per_row = frames_per_row
        self.speed = speed

        #Enemywerte
        self.max_hp = 20
        self.hp = self.max_hp
        self.invu_ms = 300
        self.hurt_until = 0
        self.meta = None
        self.quest_giver = quest_giver

        #Angriffswerte
        self.melee_range = 22
        self.contact_damage = 8
        self.attack_cooldown_ms = 800
        self.last_attack_ms = 0


        #Frames vorbereiten
        self.frames = {
            "down": self.load_frames(0),
            "left": self.load_frames(3),
            "right": self.load_frames(1),
            "up" : self.load_frames(2)
        }

        #Spritesstart
        self.direction = "down"
        self.frame_index = 0
        self.animation_timer = 0
        self.image = self.frames[self.direction][self.frame_index]
        
        #Weltposition (nicht skaliert)
        self.pos = pygame.Vector2(pos)
        self.rect = self.image.get_rect(topleft=pos)

        if movebox_inset is not None:
            self.inset = pygame.Vector2(movebox_inset)
            self.movebox = self.rect.inflate(-int(self.inset.x * 2),-int(self.inset.y * 2))
            self.movebox.center = self.rect.center

        else:
            self.inset = pygame.Vector2(0, 0)
            self.movebox = None


        #Dying Sprite
        self.state = "alive"
        self.death_frames = []
        self.death_frames_index = 0
        self.death_frames_ms = 100
        self.death_timer = 0.0

        #Attack Sprite
        self.action = "idle"
        self.attack_frames = []
        self.attack_frame_ms = 90
        self.attack_timer = 0.0
        self.attack_index = 0
        self.attack_hit_index = 1
        self.attack_has_hit = False


    def set_idle_image(self, frame=0):
        self.image = self.frames[self.direction][frame]

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

    def draw(self, surface, scale: int = 1):
        scaled_img = pygame.transform.scale(self.image,(self.image.get_width() * scale, self.image.get_height() * scale))
        surface.blit(scaled_img, (round(self.rect.x * scale), round(self.rect.y * scale)))


    def update(self, dt, player, collision_rects):
        
        if self.state == "dying":
            self.death_timer += dt * 1000
            if self.death_timer >= self.death_frames_ms:
                self.death_timer -= self.death_frames_ms
                self.death_frames_index += 1
                if self.death_frames_index >= len(self.death_frames):
                    self.kill()
                    return
                self.image = self.death_frames[self.death_frames_index]

            self.rect.topleft = (round(self.pos.x), round(self.pos.y))
            return

        if self.action == "attack":
            self.tick_attack(dt, player)
            self.rect.topleft = (round(self.pos.x), round(self.pos.y))
            return

        
        
        player_center = pygame.Vector2(player.rect.center)
        slime_center = pygame.Vector2(self.rect.center)

        distance = player_center - slime_center
        dist_len = distance.length()

        
        if dist_len < 250:

            if dist_len > 20:
                direction = distance.normalize()
                dx = direction.x * self.speed * dt
                dy = direction.y * self.speed * dt

                #Richtungssprite setzen
                if abs(direction.x) > abs(direction.y):
                    self.direction = "right" if direction.x > 0 else "left"
                else:
                    self.direction = "down" if direction.y > 0 else "up"

                #Bewegung mit Kollison
                self.move_and_collide(dx, 0, collision_rects)
                self.move_and_collide(0, dy, collision_rects)


                #Move-Animation
                self.animation_timer += dt * 1000
                if self.animation_timer > 200:
                    self.animation_timer = 0
                    self.frame_index = (self.frame_index + 1) % len(self.frames[self.direction])
                    self.image = self.frames[self.direction][self.frame_index]

            else:
                self.set_idle_image()
        else:
            self.set_idle_image()
        
        #Enemy angriff auf Player
        player_center = pygame.Vector2(player.rect.center)
        slime_center = pygame.Vector2(self.rect.center)
        if (player_center - slime_center).length() <= self.melee_range and self.action != "attack":
            self.start_attack()

    
    #Kollision prüfung
    def move_and_collide(self, dx, dy, collision_rects):
        if dx == 0 and dy == 0:
            return

        if self.movebox is not None:
            
            if dx != 0:
                self.movebox.x += dx
                for solid in collision_rects:
                    if self.movebox.colliderect(solid):
                        if dx > 0:
                            self.movebox.right = solid.left
                        else:
                            self.movebox.left = solid.right

            if dy != 0:
                self.movebox.y += dy
                for solid in collision_rects:
                    if self.movebox.colliderect(solid):
                        if dy > 0:
                            self.movebox.bottom = solid.top
                        else:
                            self.movebox.top = solid.bottom

            self.rect.center = self.movebox.center
            self.pos.update(self.rect.topleft)

        else:
            self.pos.x += dx
            self.pos.y += dy
            self.rect.topleft = (round(self.pos.x), round(self.pos.y))

            for solid in collision_rects:
                if self.rect.colliderect(solid):
                    if dx > 0:   
                        self.rect.right = solid.left
                    elif dx < 0: 
                        self.rect.left = solid.right
                    if dy > 0:   
                        self.rect.bottom = solid.top
                    elif dy < 0: 
                        self.rect.top = solid.bottom
                    self.pos.update(self.rect.topleft)


    def take_damage(self, amount):
        now = pygame.time.get_ticks()
        if now < self.hurt_until or self.state != "alive":
            return

        self.hp = max(0, self.hp - amount)
        self.hurt_until = now + self.invu_ms

        if self.hp == 0:
            self.start_death()

    def start_death(self):
        if not self.death_frames:
            self.kill()
            if hasattr(self, "meta"):
                self.meta["alive"] = False
            self.quest_giver.monster_defeated()
            return
        self.state = "dying"
        self.death_frames_index = 0
        self.death_timer = 0.0
        self.image = self.death_frames[0]
        
        if hasattr(self, "meta"):
            self.meta["alive"] = False
        self.quest_giver.monster_defeated()


    def draw_hp_bar(self, surface, scale=1):
        rx = round(self.rect.x * scale)
        ry = round(self.rect.y * scale)
        rw = self.rect.width * scale

        bar_w = max(24, int(rw * 0.7))
        bar_h = 5
        bar_x = rx + (rw - bar_w)//2
        bar_y = ry - 8

        ratio = 0 if self.max_hp == 0 else self.hp / self.max_hp
        back = pygame.Rect(bar_x, bar_y, bar_w, bar_h)
        fill = pygame.Rect(bar_x, bar_y, int(bar_w * ratio), bar_h)

        pygame.draw.rect(surface, (40, 40 ,40), back)
        pygame.draw.rect(surface, (200, 40, 40), fill)
        pygame.draw.rect(surface, (0, 0, 0), back, 1)


    def start_attack(self):
        if self.state != "alive":
            return
        if not self.attack_frames:
            self.apply_melee_damage_now()
            return
        self.action = "attack"
        self.attack_timer = 0.0
        self.attack_index = 0
        self.attack_has_hit = False
        self.image = self.attack_frames[0]

    def tick_attack(self, dt, player):
        self.attack_timer += dt * 1000
        if self.attack_timer >= self.attack_frame_ms:
            self.attack_timer -= self.attack_frame_ms
            self.attack_index += 1

            if (not self.attack_has_hit) and self.attack_index >= self.attack_hit_index:
                self.apply_melee_damage_now(player)
                self.attack_has_hit = True

            if self.attack_index >= len(self.attack_frames):
                self.action = "idle"
                self.set_idle_image()
                return

            self.image = self.attack_frames[self.attack_index]

    def apply_melee_damage_now(self, player=None):
        now = pygame.time.get_ticks()
        if now - self.last_attack_ms < self.attack_cooldown_ms:
            return
        if player is not None:
            player.take_damage(self.contact_damage)
        self.last_attack_ms = now

class Slime(Enemy):
    def __init__(self, pos, quest_giver):
        super().__init__(pos, quest_giver, "assets/Tileset/Cute_Fantasy/Enemies/Slime/Slime_Big/Slime_Big_Green.png", frame_width=64, frame_height=64, frames_per_row=8, speed=50, movebox_inset=(16,16))
        
        #Reihen in Teilset
        row_idle = 0
        row_move = 1
        row_death = 2
        row_attack = 3

        self.idle_frames = self.load_frames(row_idle, count=4)
        self.attack_frames = self.load_frames(row_attack, count=4)

        #Move-Frames
        move = self.load_frames(row_move)
        self.frames["down"] = move
        self.frames["up"] = move 
        self.frames["right"] = move
        self.frames["left"] = move

        #Death-Frames
        self.death_frames = self.load_frames(row_death)
        self.death_frames_ms = 150

        #Startbild Idle
        self.frame_index = 0
        self.image = self.idle_frames[0]

        #Slimewerte
        self.max_hp = 16
        self.hp = self.max_hp
        self.contact_damage = 5
        self.melee_range = 24

    def set_idle_image(self, frame=0):
        self.image = self.idle_frames[frame]

class Skeleton(Enemy):
    def __init__(self, pos, quest_giver):
        super().__init__(pos, quest_giver,   "assets/Tileset/Cute_Fantasy/Enemies/Skeleton/Skeleton.png", frame_width=32, frame_height=32, frames_per_row=6, speed=50)

        #Reihen in Tileset
        row_idle = 0
        row_death = 6
        row_attack = 7
        
        #Startbild idle
        self.idle_frames = self.load_frames(row_idle)
        self.image = self.idle_frames

        #Move-Frames
        self.frames["down"] = self.load_frames(3)
        self.frames["up"] = self.load_frames(2)
        self.frames["right"] = self.load_frames(1)
        self.frames["left"] = [pygame.transform.flip(f,True, False) for f in self.frames["right"]]

        #Death-Frames
        self.death_frames = self.load_frames(row_death,count=4)
        self.death_frames_ms = 150

        #Angriff-Frames
        self.attack_frames = self.load_frames(row_attack, count=4)

        #Skeletonwerte
        self.max_hp = 20
        self.hp = self.max_hp
        self.contact_damage = 8
        self.melee_range = 30


