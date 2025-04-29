import os
import sys
sys.path.append("/home/deck/Documents/blender_repo/venv/lib/python3.11/site-packages/")
import math

from contextlib import contextmanager

@contextmanager
def stdout_redirected(to=os.devnull):
    fd = sys.stdout.fileno()
    
    def _redirect_stdout(to):
        sys.stdout.close() # + implicit flush()
        os.dup2(to.fileno(), fd) # fd writes to 'to' file
        sys.stdout = os.fdopen(fd, 'w') # Python writes to fd
    
    with os.fdopen(os.dup(fd), 'w') as old_stdout:
        with open(to, 'w') as file:
            _redirect_stdout(to=file)
        try:
            yield # allow code to be run with the redirected stdout
        finally:
            _redirect_stdout(to=old_stdout)

import bpy




def parse_argv(raw_args: list[str]) -> dict:
    args = []
    kwargs = {}
    for arg in raw_args:
        if '=' in arg:
            k, v = arg.split('=')
            if v.isnumeric(): v = int(v)
            elif v.replace('.', '').isnumeric(): v = float(v)
            kwargs[k] = v
        else:
            args.append(arg)
    return args, kwargs

def render_model(
        output: str, texture: str = None,
        width: int = 1, height: int = 1,
        faces: int = 1, offset: float = 0.0,
        distance: float = 1.0, altitude: float = None,
        fov: float = 25.0, samples: int = 1,
        transparent: bool = True, mirror: bool = False,
        light_follow: bool = False, ignore_frames: list[int] = [],
        **kwargs,
    ) -> None:
    
    if altitude is None:
        altitude = distance * 1.20 # centered
    
    scene: bpy.types.Scene = bpy.data.scenes["Scene"]
    
    # Setting material
    if texture is not None:
        txtr_img = bpy.data.images.load(texture)
        node_tree = bpy.data.materials["Material"].node_tree
        node_tree.nodes["Image Texture"].image = txtr_img
    
    # Set basic camera
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.film_transparent = transparent
    scene.eevee.taa_render_samples = samples
    scene.render.image_settings.color_mode = 'RGBA'
    
    # Set camera position
    scene.camera.data.angle = math.radians(fov)
    scene.camera.rotation_mode = 'XYZ'
    scene.camera.rotation_euler[0] = math.radians(45.0)
    scene.camera.rotation_euler[1] = math.radians(0.0)
    scene.camera.location.z = altitude
    
    # Set angles
    angles = [(a*(360/faces) + offset) % 360 for a in range(faces)]
    if mirror: angles = [a for a in angles if a <= 180]
    
    # Set frames
    frame_start = bpy.context.scene.frame_start
    frame_end = bpy.context.scene.frame_end
    frames = [f for f in range(frame_start, frame_end + 1) if f not in ignore_frames]
    
    # Set light
    light = bpy.context.scene.objects["Light"]
    light.location.z = altitude
    
    print(f">>>> Rendering frame: ", end='')
    # Iterates on frames
    for frame in frames:
        print(frame, end=', ')
        bpy.context.scene.frame_set(frame)
        
        # Iterates on angles
        for angle in angles:
            # direction = int(round((270-angle)% 360, 1)*10)
            direction = int(round((360-angle)%360, 1)*10)
            arad = math.radians(angle)
            tx = distance * math.sin(arad)
            ty = - distance * math.cos(arad)
            
            if not light_follow:
                light.location.x = tx
                light.location.y = ty
            
            scene.camera.location.x = tx
            scene.camera.location.y = ty
            scene.camera.rotation_euler[2] = arad
            
            # Render and save
            with stdout_redirected():
                bpy.ops.render.render()
                bpy.data.images["Render Result"].save_render(f"{output}/f{frame:03}_d{direction:04}.png")
    print()

_, kwargs = parse_argv(sys.argv[sys.argv.index('--'):])
kwargs["ignore_frames"] = eval(kwargs["ignore_frames"])
render_model(**kwargs)
