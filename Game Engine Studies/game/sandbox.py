import os
import cv2
import numpy as np
import random
import arcade
import fnmatch
from pyglet.math import Vec2
from engine.keysystem import KeySystem
import engine.images as img

# https://www.geeksforgeeks.org/convert-opencv-image-to-pil-image-in-python/


UN_UNIT = 24

SPRITE_SCALING = 0.5
TILE_SCALING = 1.5
MOVEMENT_SPEED = 20 * UN_UNIT
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 800

CAMERA_SPEED = 0.09
VIEWPORT_MARGIN = 200

TILE_SIZE = 24

test_tiles = [
    [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, ],
    [0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, ],
    [1, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, ],
    [1, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, ],
    [1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, ],
    [0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, ],
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, ],
    [1, 0, 1, 1, 0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, ],
]

rotations = {
    0  : 3,
    90 : cv2.ROTATE_90_COUNTERCLOCKWISE,
    180: cv2.ROTATE_180,
    270: cv2.ROTATE_90_CLOCKWISE,
}

def combine_bmp(bot: cv2.typing.MatLike, top: cv2.typing.MatLike, mask: cv2.typing.MatLike, rotate: int = 0) -> cv2.typing.MatLike:
    if rotate != 0 and rotate % 90 == 0:
        rotate = (rotate + 360) % 360
        mask = cv2.rotate(mask, rotations.get(rotate))
    bot_mask = cv2.bitwise_and(bot, cv2.bitwise_not(mask))
    top_mask = cv2.bitwise_and(top, mask)
    return bot_mask + top_mask

def combine_bmp_path(bot: str, top: str, mask: str, rotate: int = 0) -> cv2.typing.MatLike:
    mask_nrm = cv2.imread(mask)
    bot_img = cv2.imread(bot)
    top_img = cv2.imread(top)
    return combine_bmp(bot_img, top_img, mask_nrm, rotate)

def slice_tiles(tile_matrix) -> dict[tuple, str]:
    subtiles = {}
    tile_order = [                  # ORDER
        (-1, -1), (-1, 0), (-1, 1), # 0 1 2
        ( 0, -1), ( 0, 0), ( 0, 1), # 3 4 5
        ( 1, -1), ( 1, 0), ( 1, 1), # 6 7 8
    ]
    width = len(tile_matrix[0])
    height = len(tile_matrix)
    
    for row in range(height):
        for col in range(width):
            tslice = []
            for r, c in tile_order:
                row_off, col_off = row + r, col + c
                if row_off < 0 or row_off >= height or col_off < 0 or col_off >= width:
                    value = '?'
                else:
                    value = str(tile_matrix[row_off][col_off])
                tslice.append(value)
            
            if tslice[1] == '1': tslice[0] = '?'; tslice[2] = '?'
            if tslice[3] == '1': tslice[0] = '?'; tslice[6] = '?'
            if tslice[5] == '1': tslice[2] = '?'; tslice[8] = '?'
            if tslice[7] == '1': tslice[6] = '?'; tslice[8] = '?'
            
            subtiles[(row, col)] = ''.join(tslice)
    return subtiles



class Tiler:
    def gen_random(self, rows: int, cols: int) -> arcade.SpriteList:
        BASE_PATH = "./projects/game/assets/transitions/"
        tilelist = [BASE_PATH + t for t in os.listdir(BASE_PATH)]
        sptlist = arcade.SpriteList(use_spatial_hash=True, is_static=True)
        for row in range(rows):
            for col in range(cols):
                chosen = random.choice(tilelist)
                tile = arcade.Sprite(chosen, scale=TILE_SCALING,
                    center_x=(col*TILE_SIZE+TILE_SIZE/2)*TILE_SCALING, center_y=(row*TILE_SIZE+TILE_SIZE/2)*TILE_SCALING)
                sptlist.append(tile)
        
        return sptlist
    
    def parse_tiles(self, tiles: list[list[int]]) -> arcade.SpriteList:
        chosen_tiles = {}
        
        v2t = {
            0: "./projects/game/assets/ground/water_normal_0.bmp",
            1: "./projects/game/assets/ground/grass_normal_0.bmp",
        }
        
        height = len(tiles)
        width = len(tiles[0])
        
        sptlist = arcade.SpriteList(use_spatial_hash=True, is_static=True)
        
        mask_names = os.listdir("./projects/game/assets/masks/processed/")
        
        for pos, trans in slice_tiles(tiles).items():
            row = pos[0]
            col = pos[1]
            chosen_tile = None
            is_edge = row == 0 or row == height-1 or col == 0 or col == width-1
            if is_edge and not trans.count('1'):
                chosen_tile = v2t[0]
            
            elif trans == '000000000':
                chosen_tile = v2t[0]
            
            elif trans[4] == '1':
                chosen_tile = v2t[1]
            
            else:
                bot = v2t[0]
                top = v2t[1]
                masks = fnmatch.filter(mask_names, f"basic_{trans}.bmp")
                masks = sorted(masks, key = lambda x: -x.count('0')) # The one with most bot
                mask = f"./projects/game/assets/masks/processed/{masks[0]}"
                
                tile_path = f"./projects/game/assets/tiles/grass_water_{masks[0]}"
                chosen_tile = tile_path
                
                tile_data = img.combine_images(
                    img.load_bitmap(bot),
                    img.load_bitmap(top),
                    img.load_bitmap(mask)
                )
                # tile_data = combine_bmp_path(bot, top, mask)
                cv2.imwrite(tile_path, tile_data)
            
            chosen_tiles[(row, col)] = chosen_tile
        
        for pos, tile_path in chosen_tiles.items():
            row = pos[0]
            col = pos[1]
            
            xpos = (col*TILE_SIZE+TILE_SIZE/2)*TILE_SCALING
            ypos = SCREEN_HEIGHT - (row*TILE_SIZE+TILE_SIZE/2)*TILE_SCALING
            
            tile = arcade.Sprite(tile_path, scale=TILE_SCALING,
                center_x = xpos,
                center_y = ypos,
            )
            sptlist.append(tile)
        return sptlist

tiler = Tiler()

class Player(arcade.Sprite):
    def on_update(self, delta_time):
        self.center_x += self.change_x * delta_time
        self.center_y += self.change_y * delta_time

class MyGame(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height)
        
        self.keysys = None
        self.player_list = None
        self.player_sprite = None
        arcade.set_background_color(arcade.color.AMAZON)
    
    def setup(self):
        self.camera_sprites = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.camera_gui = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        self.keysys = KeySystem()
        self.player_list = arcade.SpriteList()
        self.player_sprite = Player(":resources:images/animated_characters/female_person/femalePerson_idle.png", SPRITE_SCALING)
        self.player_sprite.center_x = SCREEN_WIDTH // 2
        self.player_sprite.center_y = SCREEN_HEIGHT // 2
        self.player_list.append(self.player_sprite)
        
        self.keysys.set_callback(arcade.key.E, lambda: print("Action!"))
        self.keysys.set_callback(arcade.key.SPACE, lambda: print(f"Center {self.player_sprite.center_x:.2f} {self.player_sprite.center_y:.2f}"))
        
        self.tiles = tiler.parse_tiles(test_tiles)
        
        flower_bmp = img.load_bitmap("./projects/game/assets/image/sprites/ornaments/flowers.bmp")
        flower = arcade.Sprite(
            texture=img.bitmap_to_texture_alpha(flower_bmp),
            scale=TILE_SCALING, center_x=48, center_y=48,
        )
        
        self.tiles.append(flower)
    
    def on_draw(self):
        self.clear()
        
        self.camera_sprites.use()
        self.tiles.draw(pixelated=True)
        self.player_list.draw()
        
        self.camera_gui.use()
        arcade.draw_text(f"Speed {self.player_sprite.change_x:.2f} {self.player_sprite.change_y:.2f}", 0, 400)
        arcade.draw_rectangle_filled(self.width // 2, 20, self.width, 40, arcade.color.ALMOND)
        text = f"Scroll value: ({self.camera_sprites.position[0]:5.1f}, {self.camera_sprites.position[1]:5.1f})"
        arcade.draw_text(text, 10, 10, arcade.color.BLACK_BEAN, 20)
    
    def update_player_speed(self):
        x, y = self.keysys.vector()
        self.player_sprite.change_x = x * MOVEMENT_SPEED
        self.player_sprite.change_y = y * MOVEMENT_SPEED
        
    def on_update(self, delta_time):
        # self.player_list.update()
        self.player_list.on_update(delta_time)
        self.scroll_to_player()
    
    def scroll_to_player(self):
        """
        Scroll the window to the player.
        if CAMERA_SPEED is 1, the camera will immediately move to the desired position.
        Anything between 0 and 1 will have the camera move to the location with a smoother
        pan.
        """
        position = Vec2(self.player_sprite.center_x - self.width / 2, self.player_sprite.center_y - self.height / 2)
        self.camera_sprites.move_to(position, CAMERA_SPEED)
    
    def on_key_press(self, key, modifiers):
        self.keysys.pressed(key)
        self.update_player_speed()
        
    def on_key_release(self, key, modifiers):
        self.keysys.released(key)
        self.update_player_speed()

def main():
    """ Main function """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()





































# # Generated by chatgpt
# import arcade

# # Constants
# SCREEN_WIDTH = 1280
# SCREEN_HEIGHT = 800
# TILE_SIZE = 50
# GRID_WIDTH = SCREEN_WIDTH // TILE_SIZE
# GRID_HEIGHT = SCREEN_HEIGHT // TILE_SIZE
# COLORS = [arcade.color.RED, arcade.color.BLUE, arcade.color.GREEN, arcade.color.YELLOW]

# class MyGame(arcade.Window):
#     def __init__(self, width, height):
#         super().__init__(width, height, "Simple Tile Grid")
    
#         self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    
#     def on_draw(self):
#         arcade.start_render()
#         for row in range(GRID_HEIGHT):
#             for column in range(GRID_WIDTH):
#                 x = column * TILE_SIZE
#                 y = row * TILE_SIZE
#                 color = COLORS[self.grid[row][column] % len(COLORS)]
#                 arcade.draw_rectangle_filled(x + TILE_SIZE // 2, y + TILE_SIZE // 2, TILE_SIZE, TILE_SIZE, color)
    
#     def on_mouse_press(self, x, y, button, modifiers):
#         column = x // TILE_SIZE
#         row = y // TILE_SIZE
#         if column < GRID_WIDTH and row < GRID_HEIGHT:
#             self.grid[row][column] += 1

# def main():
#     window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)
#     arcade.run()

# if __name__ == "__main__":
#     main()


