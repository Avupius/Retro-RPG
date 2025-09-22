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


quest_giver = NPC((246,104), total_monster_kills)

dungeon_enemies_data =[
    {"pos": (100,60), "type": "slime", "alive": True},
    {"pos": (555,56), "type": "slime", "alive": True},
    {"pos": (70,412), "type": "skeleton", "alive": True},]


# -- Player erstellen --
player = Player((100,80), attack_sprites = attack_sprites, enemies_group = enemies)

# -- Game Loop--
while running:

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
    
    attack_sprites.update()


    old_map = game_map
    game_map = check_interactions(player, game_map)

    if game_map != old_map:
        if game_map.name == "dungeon_map":
            for data in dungeon_enemies_data:
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

    if game_map.name == "dungeon_map":    
        for enemy in enemies:
            enemy.draw(screen, scale=screen_scale)
            enemy.draw_hp_bar(screen,scale=screen_scale)
    
    player.draw_player(screen,scale=screen_scale)
    

    for hb in attack_sprites:
        hb.draw(screen, scale=screen_scale)


    pygame.display.flip()

pygame.mixer.music.stop()
pygame.quit()
