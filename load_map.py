import pygame
import json
import os

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
        self.name = os.path.splitext(os.path.basename(map))[0]

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
        return tilesets

    def get_tile_image_by_gid(self, gid):
        if gid == 0:
            return None
        
        for ts in reversed(self.tilesets):
            if gid >= ts["firstgid"]:
                local_id = gid - ts["firstgid"]
                
                if local_id >= ts["tilecount"]:
                    return None


                columns = ts["columns"]
                x = (local_id % columns) * ts["tilewidth"]
                y = (local_id // columns) * ts["tileheight"]
                rect = pygame.Rect(x, y, ts["tilewidth"], ts["tileheight"])

                if rect.right > ts["image"].get_width() or rect.bottom > ts["image"].get_height():
                    print(f"Ungültiger GID {gid} für Tileset {ts}")
                    return None 
                
                return ts["image"].subsurface(rect)
        
        print(f"Kein Tileset gefunden {gid}")
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
