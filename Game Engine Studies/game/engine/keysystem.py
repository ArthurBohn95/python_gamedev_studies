import arcade

class KeySystem:
    def __init__(self) -> None:
        self.maps = {
            "ups"   : [arcade.key.UP,    arcade.key.W],
            "downs" : [arcade.key.DOWN,  arcade.key.S],
            "lefts" : [arcade.key.LEFT,  arcade.key.A],
            "rights": [arcade.key.RIGHT, arcade.key.D],
        }
        
        self.event_callbacks: dict[str, callable] = {}
        
        self.up_pressed   : bool = False
        self.down_pressed : bool = False
        self.left_pressed : bool = False
        self.right_pressed: bool = False
        self.other_pressed: set = set()
    
    def set_callback(self, key, callback):
        self.event_callbacks[key] = callback
    
    def pressed(self, key):
        match key:
            case k if k in self.maps["ups"]:
                self.up_pressed = True
            case k if k in self.maps["downs"]:
                self.down_pressed = True
            case k if k in self.maps["lefts"]:
                self.left_pressed = True
            case k if k in self.maps["rights"]:
                self.right_pressed = True
            case _:
                self.other_pressed.add(key)
                if key in self.event_callbacks:
                    self.event_callbacks[key]()
    
    def released(self, key):
        match key:
            case k if k in self.maps["ups"]:
                self.up_pressed = False
            case k if k in self.maps["downs"]:
                self.down_pressed = False
            case k if k in self.maps["lefts"]:
                self.left_pressed = False
            case k if k in self.maps["rights"]:
                self.right_pressed = False
            case _:
                self.other_pressed.remove(key)
    
    def vector(self, multiplier: float = 1.0, adjusted: bool = True) -> tuple[float, float]:
        x, y = 0, 0
        
        if   self.up_pressed    and not self.down_pressed:  y =  1.0
        elif self.down_pressed  and not self.up_pressed:    y = -1.0
        if   self.left_pressed  and not self.right_pressed: x = -1.0
        elif self.right_pressed and not self.left_pressed:  x =  1.0
        
        # Adjusts for correct diagonal movement with *sqrt(2)/2
        if adjusted and (x and y):
            x *= 0.70710678118
            y *= 0.70710678118
        
        return x * multiplier, y * multiplier
