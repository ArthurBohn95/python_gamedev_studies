import cv2
import arcade
import numpy as np
import PIL.Image

Mask = cv2.typing.MatLike
Image = cv2.typing.MatLike
Bitmap = cv2.typing.MatLike

_ROTS: dict[int, int] = {
    90 : cv2.ROTATE_90_COUNTERCLOCKWISE,
    180: cv2.ROTATE_180,
    270: cv2.ROTATE_90_CLOCKWISE,
}


def load_image(path: str) -> Image:
    return cv2.imread(path)

def rotate_image(image: Image, angle: int = 0) -> Image:
    """Rotations are Counter-ClockWise"""
    angle = (angle + 360) % 360
    if angle not in _ROTS: return image
    return cv2.rotate(image, _ROTS.get(angle))

def combine_images(base: Image, over: Image, mask: Mask = None) -> Image:
    if mask is None: return base + over
    base_cutout = cv2.bitwise_and(base, cv2.bitwise_not(mask))
    over_cutout = cv2.bitwise_and(over, mask)
    return base_cutout + over_cutout

def image_to_texture(image: Image) -> arcade.Texture:
    return arcade.Texture("42", image)






def load_bitmap(path: str) -> Bitmap:
    return cv2.imread(path)

def rotate_bitmap(bitmap: Bitmap, angle: int = 0) -> Bitmap:
    """Rotations are Counter-ClockWise"""
    angle = (angle + 360) % 360
    if angle not in _ROTS:
        return bitmap
    return cv2.rotate(bitmap, _ROTS.get(angle))

def combine_bitmaps(base: Bitmap, over: Bitmap, mask: Mask = None) -> Bitmap:
    if mask is None:
        return base + over
    base_cutout = cv2.bitwise_and(base, cv2.bitwise_not(mask))
    over_cutout = cv2.bitwise_and(over, mask)
    return base_cutout + over_cutout

def bitmap_to_texture(bitmap: Bitmap) -> arcade.Texture:
    img_pil = PIL.Image.fromarray(cv2.cvtColor(bitmap, cv2.COLOR_BGR2RGB))
    img_rgba = img_pil.convert("RGBA")
    texture = arcade.Texture("42", img_rgba) # name=uuid.uuid4().hex
    return texture

def bitmap_to_texture_alpha(bitmap: Bitmap) -> arcade.Texture:
    """https://stackoverflow.com/questions/70223829/opencv-how-to-convert-all-black-pixels-to-transparent-and-save-it-to-png-file"""
    alpha = np.sum(bitmap, axis=-1) > 0       # Make a True/False mask of pixels whose BGR values sum to more than zero
    alpha = np.uint8(alpha * 255)             # Convert True/False to 0/255 and change type to "uint8" to match "bitmap"
    bitmap_alpha = np.dstack((bitmap, alpha)) # Stack new alpha layer with existing image to go from BGR to BGRA, 3 to 4 channels
    img_rgba = PIL.Image.fromarray(cv2.cvtColor(bitmap_alpha, cv2.COLOR_BGRA2RGBA)) # Changes BGRA to RGBA
    texture = arcade.Texture("42", img_rgba)  # name=uuid.uuid4().hex
    return texture

def define_mask(mask: Mask) -> str:
    size = len(mask[0])
    frst = 0
    cntr = size // 2
    last = size - 1
    
    edges = [
        int(bool(e.sum())) for e in [
            mask[frst, frst], mask[frst, cntr], mask[frst, last], # 0 1 2
            mask[cntr, frst], mask[cntr, cntr], mask[cntr, last], # 3 4 5 # Should 4 always be '0'???
            mask[last, frst], mask[last, cntr], mask[last, last], # 6 7 8
        ]
    ]
    
    if edges[0] and (edges[1] or edges[3]): edges[0] = 'x'
    if edges[2] and (edges[1] or edges[5]): edges[2] = 'x'
    if edges[6] and (edges[3] or edges[7]): edges[6] = 'x'
    if edges[8] and (edges[5] or edges[7]): edges[8] = 'x'
    
    return ''.join([str(x) for x in edges])
