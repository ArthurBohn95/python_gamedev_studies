# Function to add an outline to a PNG image
# ref: https://stackoverflow.com/a/70010492

from PIL import Image, ImageFilter, ImageDraw

def add_outline(image: Image.Image, size: int = 1, color: str = "black") -> Image.Image:
    image = image.convert("RGBA")
    X, Y = image.size
    edge = image.filter(ImageFilter.FIND_EDGES).load()
    stroke = Image.new(image.mode, image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(stroke)
    for x in range(X):
        for y in range(Y):
            if edge[x,y][3] > 0:
                draw.ellipse((x-size, y-size, x+size, y+size), fill=color)
    stroke.paste(image, (0, 0), image)
    return stroke

# if __name__ == "__main__":
#     img = Image.open("./sprites/flower.png")
#     otl = add_outline(img)
#     otl.save("./sprites/flower_outline.png")


def stick(val: float, opts: set[int], loop: int = None) -> int:
    sopts = set(opts)       # limits options
    if loop is not None:
        sopts.add(loop)
        val %= loop
    vmin = min(sopts, key=lambda x: abs(x - val))
    return vmin % loop

if __name__ == "__main__":
    opts = [int(3600*(o/8)) for o in range(8)]
    print(f"{opts=}")
    for x in [-500, 0, 500, 3450, 3590, 10, 3700]:
        print(f"{x=}\t{stick(x, opts, 3600)}\t{opts}")








