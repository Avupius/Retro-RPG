import pygame

class AttackHitbox(pygame.sprite.Sprite):
    def __init__(self, owner, damage, range_px, width_px, duration_ms, direction, enemies_group):
        super().__init__()

        #Übergabeparameter für eine Hitbox
        self.owner = owner
        self.damage = damage
        self.duration_ms = duration_ms
        self.enemies_group = enemies_group
        self.spawn_time = pygame.time.get_ticks()
        self.hit_enemies = set()

        #Ablesen der massen von owner und zeichnung der Hitbox nach Richtung
        px, py, pw, ph = owner.rect
        if direction == "right":
            rect = pygame.Rect(px + pw, py + (ph - width_px)//2, range_px, width_px)
        elif direction == "left":
            rect = pygame.Rect(px - range_px, py + (ph - width_px)//2, range_px, width_px)
        elif direction == "up":
            rect = pygame.Rect(px + (pw - width_px)//2, py - range_px,width_px, range_px)
        elif direction == "down":
            rect = pygame.Rect(px + (pw - width_px)//2, py + ph, width_px, range_px)

        #Debug (Anzeige von Hitbox)
        self.image = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))

        self.rect = self.image.get_rect(topleft = rect.topleft)

    #Aktualisierung von Hitbox und enemy treffen
    def update(self, *_):
        if pygame.time.get_ticks() - self.spawn_time > self.duration_ms:
            self.kill()
            return

        for enemy in pygame.sprite.spritecollide(self, self.enemies_group, False):
            if enemy in self.hit_enemies:
                continue

            if hasattr(enemy, "take_damage"):
                enemy.take_damage(self.damage)

            self.hit_enemies.add(enemy)

    #Zeichnung von Hitbox
    def draw(self, surface, scale: int = 1):
        if scale == 1:
            surface.blit(self.image, self.rect.topleft)
        else:
            scaled_img = pygame.transform.scale(
                self.image,
                (int(self.rect.width * scale), int(self.rect.height * scale))
            )
            surface.blit(scaled_img, (round(self.rect.x * scale), round(self.rect.y * scale)))

