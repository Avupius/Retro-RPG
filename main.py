import re
from numpy import e
import pygame 
import pygame_menu
from player import Player
from npc import NPC
from enemy import Slime
from enemy import Skeleton
from npc import NPC
from load_map import LoadMap

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

def respawn(player):
    
    new_map = LoadMap("maps/home_map.json")

    #Respawn-Position
    spawn_x, spawn_y = 328, 301
    player.pos = pygame.Vector2(spawn_x, spawn_y)
    player.rect.topleft = player.pos

    player.hp = player.max_hp

    enemies.empty()
    attack_sprites.empty()

    return new_map

# -- Spiel Setup --
pygame.init()
pygame.display.set_caption("Retro RPG")
screen_scale = 2
screen_x = 640 * screen_scale
screen_y = 480 * screen_scale
screen = pygame.display.set_mode((screen_x, screen_y))
clock = pygame.time.Clock()
running = True
show_menu = True
total_monster_kills = 0
dt = 0
game_map = LoadMap("maps/start_map.json")
game_status = "running"


pygame.mixer.init()

# -- Mixer -- Hintergrund --
pygame.mixer.music.load("assets/background.mp3")
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(-1)

# -- Menü --
#menu = pygame_menu.Menu("Hauptmenü", 800, 600, theme=pygame_menu.themes.THEME_DARK, onclose=pygame_menu.events.CLOSE)
#menu.add.button("Spielen", pygame_menu.events.CLOSE)
#menu.add.button("Spiel laden")
#menu.add.button("Spiel beenden", pygame_menu.events.EXIT)

#menu.mainloop(screen)

attack_sprites =pygame.sprite.Group()

enemies = pygame.sprite.Group()


quest_giver = NPC((246,104), total_monster_kills, game_status)

dungeon_1_enemies_data =[
    {"pos": (100,60), "type": "slime", "alive": True},
    {"pos": (555,56), "type": "slime", "alive": True},
    {"pos": (70,412), "type": "skeleton", "alive": True},
    {"pos": (556,410), "type": "skeleton", "alive": True}]

dungeon_2_enemies_data= [
    {"pos": (312, 371), "type": "slime", "alive": True},
    {"pos": (614, 381), "type": "skeleton", "alive": True},
    {"pos": (546, 77), "type": "slime", "alive": True},
    {"pos": (86, 87), "type": "skeleton", "alive": True}]

# -- Player erstellen --
player = Player((100,80), attack_sprites = attack_sprites, enemies_group = enemies)

# -- Game Loop--
while running:

    if game_status == "running":
        # Frames Berechnung
        dt = clock.tick(60) / 1000

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                        if game_map.name == "town_map" and player.rect.colliderect(quest_giver.rect):
                            quest_giver.interact(player)
            if event.type == pygame.QUIT:
                running = False
        
        screen.fill((0, 0, 0))

        # Player movment & Kollsion
        collision_rects = game_map.get_collision_rects()
        player.update(dt, collision_rects)

        if player.hp <= 0:
            game_map = respawn(player)
        
        attack_sprites.update()

        old_map = game_map
        game_map = check_interactions(player, game_map)

        if game_map != old_map:
            enemies.empty()

            if game_map.name == "dungeon_map_1":
                for data in dungeon_1_enemies_data:
                    if data["alive"]:
                        if data["type"] == "slime":
                            enemy = Slime(data["pos"],quest_giver)
                        elif data["type"] == "skeleton":
                            enemy = Skeleton(data["pos"], quest_giver)
                        enemies.add(enemy)
                        enemy.meta = data

            elif game_map.name == "dungeon_map_2":
                for data in dungeon_2_enemies_data:
                    if data["alive"]:
                        if data["type"] == "slime":
                            enemy = Slime(data["pos"],quest_giver)
                        elif data["type"] == "skeleton":
                            enemy = Skeleton(data["pos"], quest_giver)
                        enemies.add(enemy)
                        enemy.meta = data

        for enemy in enemies:
            enemy.update(dt, player, collision_rects)

        # Bildshirm zeichen
        screen.fill((0, 0, 0))
        game_map.draw(screen)
        
        if game_map.name == "town_map":
            quest_giver.draw(screen, scale=screen_scale)

        if game_map.name == "dungeon_map_1" or game_map.name == "dungeon_map_2":    
            for enemy in enemies:
                enemy.draw(screen, scale=screen_scale)
                enemy.draw_hp_bar(screen,scale=screen_scale)
        
        player.draw_player(screen,scale=screen_scale)
        
        for hb in attack_sprites:
            hb.draw(screen, scale=screen_scale)

        pygame.display.flip()


        if quest_giver.quest_completed and quest_giver.completed_at:
            if pygame.time.get_ticks() - quest_giver.completed_at > 5000:
                game_status = "completed"

    elif game_status == "completed":
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                running = False

        screen.fill((0, 0, 0))
        font = pygame.font.SysFont("Arial", 48, bold=True)
        text = font.render("GAME COMPLETED!", True, (255, 255, 255))
        rect = text.get_rect(center=(screen_x //2, screen_y //2))
        screen.blit(text, rect)

        font_small = pygame.font.SysFont("Arial", 24)
        hint = font_small.render("Drücke Q zum Beenden", True, (255, 255, 255))
        rect_hint = hint.get_rect(center=(screen_x // 2, rect.bottom + 40))
        screen.blit(hint, rect_hint)

        pygame.display.flip()

pygame.mixer.music.stop()
pygame.quit()
