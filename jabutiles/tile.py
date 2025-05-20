from typing import Self, Literal

import numpy as np
from PIL import Image, ImageOps, ImageDraw, ImageChops, ImageFilter, ImageEnhance

from jabutiles.utils import coalesce, clamp
from jabutiles.configs import Shapes



class Tile:
    """A framework to deal with Tiles"""
    
    # DUNDERS # ----------------------------------------------------------------
    def __init__(self,
            ref: str | Image.Image | np.typing.NDArray = None,
            shape: Shapes = None,
        ) -> None:
        """The base Tile class for tiling operations
        
        Returns:
            Tile: A PIL.Image wrapped around tiling methods
        """
        
        self.image: Image.Image
        
        if isinstance(ref, Image.Image):
            self.image = ref
        
        elif isinstance(ref, str):
            self.image = Image.open(ref)
        
        elif isinstance(ref, np.ndarray):
            self.image = Image.fromarray(ref)
        
        else:
            self.image = Image.new('RGB', (1, 1), (255, 0, 255))
        
        
        if shape is None:
            w, h = self.size
            shape = 'ort.square' if w == h else 'ort.rect'
        
        self.shape: str = shape
    
    def __repr__(self):
        try:
            display(self.image) # type: ignore
        
        finally:
            return f"size:{self.size} mode:{self.mode} shape:{self.shape}"
    
    # PROPERTIES # -------------------------------------------------------------
    @property
    def mode(self) -> str:
        return self.image.mode
    
    @property
    def size(self) -> tuple[int, int]:
        return self.image.size
    
    @property
    def center(self) -> tuple[float, float]:
        size = self.size
        return size[0]/2, size[1]/2
    
    @property
    def as_mask(self) -> Self:
        """Returns the Tile as a mask (only L channel).
        Useful to ensure a mask is indeed a mask.
        
        Returns:
            Tile: The converted Tile.
        """
        
        return Tile(self.image.convert('L'))
    
    @property
    def as_array(self) -> np.typing.NDArray:
        """Returns the Tile as a numpy array.
        Useful for matrix operations.
        
        Returns:
            np.ndarray: The numpy array.
        """
        
        return np.array(self.image)
    
    # METHODS # ----------------------------------------------------------------
    def copy(self) -> Self:
        return Tile(self.image.copy(), self.shape)
    
    def display(self,
            factor: float = 1.0,
            resample: Image.Resampling = Image.Resampling.NEAREST,
        ) -> None:
        
        display(ImageOps.scale(self.image, factor, resample)) # type: ignore
    
    def invert(self) -> Self:
        """'invert' as in 'negative'"""
        
        image = ImageOps.invert(self.image)
        
        return Tile(image, self.shape)
    
    def rotate(self, angle: int, expand: bool = True) -> Self:
        if self.shape == "iso" and angle == 90:
            pass
        
        image = self.image.rotate(int(angle), expand=expand)
        
        return Tile(image, self.shape)
    
    def mirror(self, axis: Literal['|', '-', '/', '\\']) -> Self:
        """Mirrors the Tile in the horizontal, vertical or diagonal directions.  
        
        Args:
            axis ('-', '|', '/', '\\'): Which axis to mirror the image.
        
        Returns:
            Tile: The mirrored Tile.
        """
        
        match axis:
            case '-':  image = ImageOps.flip(self.image)
            case '|':  image = ImageOps.mirror(self.image)
            case '\\': image = self.image.transpose(Image.Transpose.TRANSPOSE)
            case '/':  image = self.image.transpose(Image.Transpose.TRANSVERSE)
            case _:    image = self.image.copy()
        
        return Tile(image, self.shape)
    
    def scale(self,
            factor: float | tuple[float, float],
            resample: Image.Resampling = Image.Resampling.NEAREST,
        ) -> Self:
        """'scale' as in 'stretch by factor(x,y) or factor(x==y)'"""
        
        if isinstance(factor, (int, float)):
            image = ImageOps.scale(self.image, factor, resample)
        
        elif isinstance(factor, tuple):
            newsize = (
                int(self.size[0] * factor[0]),
                int(self.size[1] * factor[1]))
            image = self.image.resize(newsize, resample)
        
        else:
            print(f"Strange parameters")
            image = self.image.copy()
        
        return Tile(image, self.shape)
    
    def filter(self,
            filters: ImageFilter.Filter | list[ImageFilter.Filter],
            padding: int = 4,
        ) -> Self:
        
        w, h = self.size
        
        # Pads the image with itself to avoid filter bleeding
        image = self.take((w-padding, h-padding), (w+padding*2, h+padding*2)).image
        
        filters = coalesce(filters, list)
        for f in filters:
            image = image.filter(f)
        
        # Crops the extra border, restoring the original size
        image = ImageOps.crop(image, padding)
        
        return Tile(image, self.shape)
    
    def brightness(self, factor: float = 1.0) -> Self:
        image = ImageEnhance.Brightness(self.image).enhance(factor)
        
        return Tile(image, self.shape)
    
    def color(self, factor: float = 1.0) -> Self:
        image = ImageEnhance.Color(self.image).enhance(factor)
        
        return Tile(image, self.shape)
    
    def contrast(self, factor: float = 1.0) -> Self:
        image = ImageEnhance.Contrast(self.image).enhance(factor)
        
        return Tile(image, self.shape)
    
    def enhance(self, enhancer: ImageEnhance._Enhance, factor: float = 1.0) -> Self:
        image = enhancer(self.image).enhance(factor)
        
        return Tile(image, self.shape)
    
    def cutout(self, mask: Self) -> Self:
        """'cutout' as in 'cookie cutter'"""
        
        image = self.image.copy()
        image.putalpha(mask.as_mask.image)
        
        return Tile(image, mask.shape)
    
    def crop(self, box: tuple[int, int, int, int]) -> Self:
        image = self.image.crop(box)
        
        return Tile(image, self.shape)
    
    def take(self, pos: tuple[int, int], size: tuple[int, int]) -> Self:
        x0, y0 = pos
        width, height = size
        wrap_width, wrap_height = self.size
        
        xidx = (np.arange(x0, x0+width)  % wrap_width)
        yidx = (np.arange(y0, y0+height) % wrap_height)
        
        crop = self.as_array[np.ix_(yidx, xidx)]
        
        return Tile(crop)
    
    def offset(self, offset: tuple[int, int]) -> Self:
        width, height = self.size
        offx, offy = offset
        
        posx = (width - offx) % width
        posy = (height - offy) % height
        
        return self.take((posx, posy), self.size)
    
    def multiply(self, color_tile: Self) -> Self:
        image = ImageChops.multiply(self.image, color_tile.image)
        
        return Tile(image, self.shape)
    
    def outline(self,
            thickness: float = 1.0,
            color: str | tuple[int, int, int] = "black",
            combine: bool = True,
        ) -> Self:
        
        ref_image = self.image.convert("RGBA")
        base_image = Image.new(ref_image.mode, ref_image.size, (0, 0, 0, 0))
        canvas = ImageDraw.Draw(base_image)
        
        # Ensures thickness is always at least 1
        T = clamp(thickness, (1, 1000))
        W, H = ref_image.size
        edge = ref_image.filter(ImageFilter.FIND_EDGES).load()
        
        for x in range(W):
            for y in range(H):
                if not edge[x,y][3]:
                    continue
                
                if T % 1 == 0: # 1, 2, 3, ...round corners
                    canvas.ellipse((x-T, y-T, x+T, y+T), fill=color)
                
                else: # 1.5, 2.5, 3.5, ... square corners
                    canvas.rectangle((x-T+0.5, y-T+0.5, x+T-0.5, y+T-0.5), fill=color)
        
        if combine:
            base_image.paste(ref_image, mask=ref_image)
        
        else:
            alpha = ImageEnhance.Brightness(ref_image).enhance(256)
            base_image = ImageChops.subtract(base_image, alpha)
        
        return Tile(base_image, self.shape)


