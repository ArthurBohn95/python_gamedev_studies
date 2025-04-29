# ./venv/bin/python ./run_renders.py

import os
import subprocess
import pandas as pd

def clear_folder(path: str) -> None:
    for filename in os.listdir(path):
        os.remove(os.path.join(path, filename))

BASE_PATH = "/home/deck/Documents/blender_repo"
textures_folder = f"{BASE_PATH}/assets/textures"
output_folder = f"{BASE_PATH}/assets/renders"
parameters_folder = f"{BASE_PATH}/assets/renders/parameters.csv"
render_params = pd.read_csv(parameters_folder, sep=';').fillna(value='')

# render_only: list[str] = ["default_cube", "monke"]
render_only: list[str] = render_params["name"].to_list()

for params in render_params.to_dict(orient="records"):
    name = params.pop("name")
    if name not in render_only:
        continue
    print(f"\n>>>> Model Name: '{name}'")
    
    texture = params.pop("texture")
    if texture:
        print(f">>>> Texture: {texture}")
        params["texture"] = f"{textures_folder}/{texture}"
    
    output = params.pop("output")
    folder = f"{output_folder}/{output}"
    params["output"] = folder
    print(f">>>> Output Folder: {folder}")
    
    if not os.path.exists(folder):
        os.makedirs(folder)
    clear_folder(folder)
    
    kwargs = ' '.join([f"{k}={v}" for k, v in params.items()])
    cmd = f"flatpak run org.blender.Blender ~/Documents/blender_repo/assets/models/{name}.blend -b -P ~/Documents/blender_repo/blender_pipeline.py -- {kwargs}"
    subprocess.run(cmd, shell=True, executable="/bin/bash")
