

from PIL import Image, ImageDraw, ImageOps, ImageEnhance

from jabutiles.tile import Tile
from jabutiles.utils import combine_choices



class TileOps:
    # STATIC METHODS # ---------------------------------------------------------
    @staticmethod
    def create_symmetrical_outline(
            size: tuple[int, int],
            lines: list[tuple[tuple[float]]],
            **kwargs,
        ) -> Image.Image:
        
        image = Image.new("L", size, 0)
        draw  = ImageDraw.Draw(image)
        
        for line in lines:
            draw.line(line, fill=255)
        
        image.paste(ImageOps.flip(image), mask=ImageOps.invert(image))
        image.paste(ImageOps.mirror(image), mask=ImageOps.invert(image))
        
        return image
    
    @staticmethod
    def create_mask_from_outline(
            base: Image.Image,
            **kwargs,
        ) -> Image.Image:
        
        mask = base.copy()
        width, height = mask.size
        
        ImageDraw.floodfill(mask, (width / 2, height / 2), 255)
        
        return mask
    
    @staticmethod
    def overlay_tiles(base: Tile, head: Tile, mask: Tile = None, alpha: float = 0.5) -> Tile:
        """Merges two tiles into a new one.
        Must have a MASK or alpha value (default, 0.5).
        
        If using a MASK, it must have the same dimensions as both DATA Tiles.
        The pixel values from the MASK range from 0 (full base) to 255 (full head).
        
        The alpha value is used if no MASK is present.
        Its value is applied to the Tiles as a whole, not by pixel.
        
        Args:
            base (Tile): The Tile that goes on the bottom.
            head (Tile): The Tile that goes on top.
            mask (Tile, optional): A special Tile that controls how each pixel is merged. Defaults to None.
            alpha (float, optional): A value that controls how all pixels are merged. Defaults to 0.5.
        
        Returns:
            Tile: A new Tile resulting from the combination of both Tiles.
        """
        
        if mask is None:
            image = Image.blend(base.image, head.image, alpha)
            shape = base.shape
        
        else:
            image = Image.composite(head.image, base.image, mask.as_mask.image)
            shape = mask.shape
        
        return Tile(image, shape)
    
    @staticmethod
    def merge_tiles(*tiles: tuple[Tile, Tile]) -> Tile:
        """
        tiles = [(tile, mask), (tile, mask), ...]
        """
        REFTILE = tiles[0][0]
        REFMASK = tiles[-1][1]
        SIZE = REFTILE.size
        
        image = Image.new('RGBA', SIZE, (0, 0, 0, 0))
        
        for tile, mask in tiles:
            image.paste(tile.image, mask=mask.as_mask.image)
        
        return Tile(image, REFMASK.shape)
    
    @staticmethod
    def merge_masks(*masks: Tile) -> Tile:
        """Adds several MASKs together.
        Their values are combined with bitwise OR.
        
        Returns:
            Tile: A single Tile MASK
        """
        
        assert len(masks) >= 2, "Insufficient masks to be merged (<2)"
        
        base = masks[0].as_mask.as_array
        
        for mask in masks[1:]:
            base |= mask.as_mask.as_array
        
        return Tile(base, masks[-1].shape)
    
    @staticmethod
    def combine_masks(
            mask_info: dict[str, Tile]
        ) -> tuple[str, Tile]:
        """ Combine the masks' data AND their neighbours' information"""
        
        assert len(mask_info) >= 2, "Insufficient masks to be combined (<2)"
        
        mask_data = mask_info.copy()
        base_edge, base_mask = mask_data.popitem()
        
        for edge, mask in mask_data.items():
            base_edge = combine_choices(base_edge, edge)
            base_mask = TileOps.merge_masks(base_mask, mask)
        
        return base_edge, base_mask
    
    @staticmethod
    def shade_tile(
            base: Tile,
            pattern_mask: Tile,
            offset: tuple[int, int],
            brightness: float = 1.0,
            inverted: bool = False,
        ) -> Tile:
        
        offset_mask = pattern_mask.offset(offset).invert()
        base_adjusted = base.enhance(ImageEnhance.Brightness, brightness)
        
        if inverted: # inverts which is overlaid on the other for double shades
            base, base_adjusted = base_adjusted, base
        
        base_shaded = TileOps.overlay_tiles(base, base_adjusted, offset_mask)
        
        return base_shaded
