import os
import json
import math
import utils
import arcade



def parse_direc_frame(filename: str) -> tuple[int|None, int]:
    filename = filename.split('.')[0]
    tokens = filename.split('_') if '_' in filename else [filename]
    
    direc, frame = None, 0
    for token in tokens:
        if not token[1:].isnumeric():
            continue
        if token.startswith('d'): direc = int(token[1:])
        if token.startswith('f'): frame = int(token[1:])
    return direc, frame


class AnimationData:
    def __init__(self, folder: str) -> None:
        self.folder: str = folder
        self.modelname: str = ""
        self.textures: dict[tuple[int|None, int], arcade.Texture] = {}
        self.keyframes: dict[str, dict[str, dict]] = {}
        
        self._parse_model_name()
        self._load_textures()
        self._load_keyframes()
    
    def _parse_model_name(self):
        self.folder = self.folder.replace('\\', '/').removesuffix('/')
        self.modelname = self.folder.split('/')[-1]
    
    def _load_textures(self):
        for filename in os.listdir(self.folder):
            ext = filename.split('.')[-1]
            if not ext in ('png', 'bmp'):
                continue
            framekey = parse_direc_frame(filename)
            filepath = f"{self.folder}/{filename}"
            texture = arcade.load_texture(filepath)
            self.textures[framekey] = texture
    
    def _load_keyframes(self):
        keyframe_path = f"{self.folder}/_keyframes.json"
        if not os.path.exists(keyframe_path):
            print(f"! The keyframe file for '{self.modelname}' is missing.\nShould be {keyframe_path}")
            return
        
        with open(keyframe_path, 'r') as injson:
            keyframes: dict[str, dict] = json.load(injson)
        
        for statename, state in keyframes["states"].items():
            # If each frame's duration is not specified, a global one is assigned
            if not isinstance(state["delay"], list):
                state["delay"] = [state["delay"]] * len(state["frames"])
            
            # [0, 1, 2, 3] -invert> [3, 2, 1, 0] -trim> [_, 2, 1, _] -join> [0, 1, 2, 3, 2, 1]
            if state["type"] == "bounce":
                state["delay"] += state["delay"][::-1][1:-1]
                state["frames"] += state["frames"][::-1][1:-1]
            state["length"] = len(state["frames"])
            
            # In the case the length of frames and delays are not the same
            if len(state["delay"]) != len(state["frames"]):
                print(f"Model's '{self.modelname}' state '{statename}' is wrong")
            
            self.keyframes = keyframes


class AnimationManager:
    def __init__(self, animations_folder: str) -> None:
        self.folder: str = animations_folder
        self.animations: dict[str, AnimationData] = {}
    
    def load_model(self, model: str) -> None:
        if model in self.animations:
            print(f"! Model '{model}' is already loaded")
            return
        
        print(f"+ Loading model '{model}'")
        model_folder = f"{self.folder}/{model}"
        animation = AnimationData(model_folder)
        self.animations[model] = animation
    
    def load_models(self, models: list[str]) -> None:
        for model in models:
            self.load_model(model)
    
    def load_all_models(self) -> None:
        for model in os.listdir(self.folder):
            self.load_model(model)
    
    def unload_model(self, model: str) -> None:
        self.animations.pop(model, None)
    
    def get(self, model: str) -> AnimationData:
        return self.animations.get(model)


class AnimatedSprite(arcade.Sprite):
    def __init__(self, animation_data: AnimationData,) -> None:
        super().__init__()
        self.cur_state: str = None
        self.cur_angle: float = 0
        self.cur_direction: int = 0
        self.change_d: float = 0
        self.cur_frame_index: int = 0
        self.cur_frame_tally: float = 0
        
        self.something_changed: bool = False
        self.defer_state_change: bool = False
        
        self.target_pos: tuple[float, float] = None
        self.has_target_pos: bool = False
        self.target_pos_margin: float = 0.0
        self.speed: float = 0.0
        
        # Locks
        self.direction_locked: bool = False # Cannot auto change direction
        self.state_locked: bool = False     # Cannot auto change state
        
        self.animation: AnimationData = animation_data
        self.configs = self.animation.keyframes.get("configs", {})
        
        self.is_time_based: bool = self.configs.get("time_based", True)
        
        rots = self.configs.get("directions", None)
        if rots is not None and rots > 1:
            self.direction_locked = False
            self.directions: set[int] = {int(3600*a/rots) for a in range(rots)}
        else:
            self.direction_locked = True
            self.cur_direction = None
        
        hitbox = self.configs.get("hitbox", (0, 0, 10, 10))
        self.set_hit_box(arcade.get_rectangle_points(*hitbox))
        
        self.update_animation()
    
    def go_to(self, position: tuple[float, float], speed: float = 1, margin: float = 10) -> None:
        self.target_pos = position
        self.has_target_pos = True
        self.target_pos_margin = margin
        self.speed = speed
        
        self.check_target()
    
    def check_target(self):
        if not self.has_target_pos:
            return
        
        x_diff = self.target_pos[0] - self.center_x
        y_diff = self.target_pos[1] - self.center_y
        angle = math.atan2(y_diff, x_diff)
        
        self.change_x = math.cos(angle) * self.speed
        self.change_y = math.sin(angle) * self.speed
    
    def _check_distance_to_target(self):
        if arcade.get_distance(*self.position, *self.target_pos) <= self.target_pos_margin:
            self.has_target_pos = False
            self.target_pos = None
            self.stop()
    
    def change_state(self, state: str, lock: bool = False) -> None:
        if self.cur_state != state:
            self.cur_state = state
            self.something_changed = True
        if lock:
            self.state_locked = True
    
    def _cur_state_info(self) -> dict:
        return self.animation.keyframes["states"][self.cur_state]
    
    def on_update(self, delta_time: float = 1 / 60):
        self.angle = 0
        
        if self.has_target_pos:
            self._check_distance_to_target()
        
        self.center_x += self.change_x * delta_time
        self.center_y += self.change_y * delta_time
        self.cur_angle += self.change_d * delta_time
        self.update_animation(delta_time)
    
    def update_state(self) -> None:
        if self.state_locked:
            return
        
        # State logic can change drastically from model to model, must override
        last_state = self.cur_state
        
        # ... logic here ...
        if self.change_x or self.change_y:
            self.cur_state = "move"
        else:
            self.cur_state = "idle"
        
        if last_state != self.cur_state:
            self.defer_state_change = True
    
    def update_frame(self, delta_time: float) -> None:
        state_info = self._cur_state_info()
        
        if self.defer_state_change:
            self.defer_state_change = False
            self.something_changed = True
            self.cur_frame_index = 0
            self.cur_frame_tally = 0
        
        frame_limit = state_info["delay"][self.cur_frame_index]
        
        if self.cur_frame_tally >= frame_limit:
            if self.is_time_based:
                self.cur_frame_tally -= frame_limit
            else:
                self.cur_frame_tally = 0
            
            self.cur_frame_index = (self.cur_frame_index + 1) % state_info["length"]
            self.something_changed = True
        
        if self.is_time_based:
            self.cur_frame_tally += delta_time
        else:
            self.cur_frame_tally += 1
    
    def update_direc(self) -> None:
        if self.direction_locked:
            return
        
        last_direc = self.cur_direction
        
        if self.cur_state in ('idle'):
            return
        else:
            self.cur_angle = math.atan2(self.change_y, self.change_x)
        
        direc = 10 * math.degrees(self.cur_angle)
        self.cur_direction = utils.stick(direc, self.directions, 3600)
        if last_direc != self.cur_direction:
            self.something_changed = True
    
    def update_texture(self) -> None:
        direc = self.cur_direction
        frame = self._cur_state_info()["frames"][self.cur_frame_index]
        self.texture = self.animation.textures.get((direc, frame))
    
    def update_animation(self, delta_time: float = 1/60) -> None:
        self.something_changed = False
        self.update_state()
        self.update_frame(delta_time)
        self.update_direc()
        
        if self.something_changed:
            self.update_texture()
