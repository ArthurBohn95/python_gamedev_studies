import random
import arcade
arcade.enable_timings()
from engine.animation_wp import AnimationManager, AnimatedSprite

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 800
MIDDLE_SCREEN = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
MOVEMENT_SPEED = 50
ROTATION_SPEED = 2
SPRITE_SCALE = 1
SEPARATION = 100 * SPRITE_SCALE
TPS = 10
TICK_LAPSE = 1/TPS

default_texture = arcade.load_texture("./rotsys/sprites/default.png")
anmgr = AnimationManager("./rotsys/sprites/animations")
anmgr.load_models(["monke3"])
# anmgr.load_all_models()

# X, Y = 40, 25 # 1000
# X, Y = 32, 16 # 512
X, Y = 8, 4
coords = []
for x in range(X):
    for y in range(Y):
        coords.append((x - X/2, y - Y/2))



class MyGame(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.tick_sum: float = 0
        self.tick_count: int = 0
    
    def setup(self):
        arcade.set_background_color(arcade.color.AIR_SUPERIORITY_BLUE)
        
        self.physics_engine : arcade.PymunkPhysicsEngine = arcade.PymunkPhysicsEngine()
        self.general_sprites = arcade.SpriteList()
        
        for c in coords:
            spt = AnimatedSprite(anmgr.get("monke3"))
            spt.set_position(SCREEN_WIDTH  // 2 + SEPARATION * c[0], SCREEN_HEIGHT // 2 + SEPARATION * c[1])
            spt.scale = SPRITE_SCALE
            self.general_sprites.append(spt)
        
        self.physics_engine.add_sprite_list(self.general_sprites, moment_of_intertia=arcade.PymunkPhysicsEngine.STATIC, collision_type="monke")
    
    def on_draw(self):
        self.clear()
        self.general_sprites.draw(pixelated=True)
        self.general_sprites.draw_hit_boxes()
        arcade.draw_text(f"FPS: {arcade.get_fps(60):5.1f}", 10, 10, arcade.color.BLACK, 20)
    
    def on_update(self, delta_time: float = 1/60):
        self.tick_sum += delta_time
        if self.tick_sum >= TICK_LAPSE:
            self.tick_sum -= TICK_LAPSE
            self.on_tick()
        
        self.general_sprites.on_update(delta_time)
        self.physics_engine.step(delta_time)
    
    def on_tick(self):
        self.tick_count += 1
        match self.tick_count % TPS:
            case 0 | 5: self.__sort_lists()
            # case 1 | 6: self.__handle_collisions()
            case 9    : self.__monke_check()
            case _    : self.__monke_do()
    
    def __sort_lists(self):
        self.general_sprites.sort(key=lambda x: x.bottom)
    
    def __monke_check(self):
        for spt in self.general_sprites:
            spt.check_target()
    
    def __monke_do(self):
        idx = random.randint(0, len(self.general_sprites)-1)
        spt = self.general_sprites[idx]
        if not spt.has_target_pos:
            gtx = random.randrange(0, SCREEN_WIDTH)
            gty = random.randrange(0, SCREEN_HEIGHT)
            self.general_sprites[idx].go_to((gtx, gty), MOVEMENT_SPEED, 10)
            self.physics_engine.apply_force(spt, (spt.change_x*10, spt.change_y*10))
            
    
    # def __handle_collisions(self):
    #     pass
        # for spt in self.general_sprites:
        #     cols = arcade.check_for_collision_with_list(spt, self.general_sprites)
        #     for col in cols:
        #         sx, sy = spt.position
        #         cx, cy = col.position
        #         mx = abs(cx - sx) * spt.change_x
        #         my = abs(cy - sy) * spt.change_y
        #         spt.center_x -= mx / 10
        #         spt.center_y -= my / 10
        # pass



def main():
    """ Main function """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    window.setup()
    window.set_vsync(True)
    # window.set_location(0, 20)
    arcade.run()

if __name__ == "__main__":
    main()
