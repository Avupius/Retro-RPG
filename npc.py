import pygame

class NPC(pygame.sprite.Sprite):
    def __init__(self, pos, current_kills, spritesheet_path="assets/Tileset/Cute_Fantasy/villager/Farmer_Bob.png", frame_width=64, frame_height=64, frames_per_row = 4):
        super().__init__()

        self.spritesheet = pygame.image.load(spritesheet_path).convert_alpha()
        
        #Frame Einstellungen
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.frames_per_row = frames_per_row
        
        #statisches Frame
        self.image = self.load_frames(0,1)[0]
        self.rect = self.image.get_rect(topleft=pos)


        #Quest Status
        self.quest_qiven = False
        self.quest_completed = False
        self.required_kills = 3
        self.current_kills = current_kills

        #Textanzeige
        self.font = pygame.font.SysFont("Arial", 16)
        self.current_text = None
        self.text_timer = 800


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


    def interact(self, player):
        if not self.quest_qiven:
            self.show_text(f"Bitte besige {self.required_kills} Monster, die befinden sich nordlich von deinen Haus in einen Dungeon")
            self.quest_qiven = True
        
        elif not self.quest_completed:
            if self.current_kills >= self.required_kills:
                self.show_text(f"Wunderbar, unser Dorf ist jetzt sicher!!!")
                self.quest_completed = True
                #TODO Game abschlissen
            else:
                self.show_text(f"Was machst du noch hier? Du muss noch {self.required_kills - self.current_kills} Monster besiegen!!!")

    def show_text(self, text, duration=2000):
        self.current_text = self.font.render(text, True, (0, 0, 0))
        self.text_timer = pygame.time.get_ticks() + duration

    def monster_defeated(self):
        if not self.quest_completed:
            self.current_kills += 1

    def draw(self, surface, scale: int = 1):
        scaled_img = pygame.transform.scale(self.image,(self.image.get_width() * scale, self.image.get_height() * scale))
        surface.blit(scaled_img, (round(self.rect.x * scale), round(self.rect.y * scale)))

        screen_w, screen_h = surface.get_size()

        if self.current_text and pygame.time.get_ticks() < self.text_timer:
            text_rect = self.current_text.get_rect(center=(screen_w // 2, screen_h - 40))

            bubble_rect = text_rect.inflate(10 * scale, 6 * scale)
            pygame.draw.rect(surface, (255, 255, 255), bubble_rect, border_radius=5)
            pygame.draw.rect(surface, (0, 0, 0), bubble_rect, 2, border_radius=5)

            surface.blit(self.current_text, text_rect)

        else:
            self.current_text = None

