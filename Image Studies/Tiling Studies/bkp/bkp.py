def create_isometric_outline(size: int, **kwargs) -> Image.Image:
    assert size % 2 == 0, "Size must be even numbered"
    
    lines = [
        ((0, size/2-1), (size-1, 0)), #diagonal
    ]
    return create_symmetrical_outline((size*2, size), lines, **kwargs)

iso = create_isometric_outline(24)
display_image(iso, 8)
isomask = create_mask_from_outline(iso)
display_image(isomask, 8)

def create_hexagonal_outline(
        size: int | tuple[int, int],
        top: Literal["flat", "point"] = "flat",
        **kwargs
    ) -> Image.Image:
    
    if isinstance(size, int):
        assert size % 2 == 0, "Size must be even numbered"
        
        SQRT3BY2 = 0.866
        size = size, int(snap(size*SQRT3BY2, 4)) # nearest multiple of 4
    
    # It's easier to always create as flat top and rotate later
    width, height = size
    
    prop = height/width
    print(f"{prop=:.2f} ({100*prop/SQRT3BY2:.0f}%)")
    
    # Markers (Q.uarter, M.iddle)
    QW, MW = width/4, width/2
    QH, MH = height/4, height/2
    
    # Small correction for widths 8 and 12 (heavy outlier)
    if width in (8, 12):
        QW += 0.5
    
    print(f"{QW=} {MW=} {QH=} {MH=} ")
    
    lines = [
        ((0.5, MH-0.5), (QW-0.5, 0.5)), # top-left diagonal
        ((QW+0.5, 0.5), (MW, 0.5)), # top line
    ]
    
    base = create_symmetrical_outline((width, height), lines, **kwargs)
    
    if top == 'point':
        base = base.rotate(90, expand=True)
    
    print(f"{base.size=}")
    return base

SIZE = 26

hexa = create_hexagonal_outline(SIZE, 'flat')
display_image(hexa, 10)
hexamask = create_mask_from_outline(hexa)
display_image(hexamask, 10)

hexa = create_hexagonal_outline(SIZE, 'point')
display_image(hexa, 10)
hexamask = create_mask_from_outline(hexa)
display_image(hexamask, 10)

# BEST ONES: 14, 18, 22, 26, 32, 36, 44

def create_orthogonal_outline(size: int | tuple[int, int], **kwargs) -> Image.Image:
    if isinstance(size, int):
        size = (size, size)
    
    w, h = size
    
    lines = [
        ((0, 0), (0, h-1)), # left
        ((0, 0), (w-1, 0)), # top
    ]
    return create_symmetrical_outline(size, lines, **kwargs)

ortho = create_orthogonal_outline(24)
display_image(ortho, 8)
orthomask = create_mask_from_outline(ortho)
display_image(orthomask, 8)





















class SimpleTile:
    def __init__(self, ref: str | Image.Image | np.typing.NDArray):
        
        self.image: Image.Image
        if isinstance(ref, Image.Image):
            self.image = ref
        elif isinstance(ref, str):
            self.image = Image.open(ref)
        elif isinstance(ref, np.ndarray):
            self.image = Image.fromarray(ref)
    
    @staticmethod
    def from_path(path: str) -> "SimpleTile":
        return SimpleTile(Image.open(path))
    
    @staticmethod
    def from_array(array: np.typing.NDArray) -> "SimpleTile":
        return SimpleTile(Image.fromarray(array))
    
    @staticmethod
    def merge(base: "SimpleTile", head: "SimpleTile", mask: "SimpleTile" = None, alpha: float = 0.5) -> "SimpleTile":
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
        
        else:
            image = Image.composite(base.image, head.image, mask.as_mask.image)
        
        return SimpleTile(image)
    
    @staticmethod
    def merge_masks(*masks: "SimpleTile") -> "SimpleTile":
        """Adds several MASKs together.
        Their values are combined with bitwise OR.
        
        Returns:
            Tile: A single SimpleTile MASK
        """
        
        assert len(masks) >= 2, "Insufficient masks to be merged (<2)"
        
        base = masks[0].as_mask.as_array
        
        for mask in masks[1:]:
            base |= mask.as_mask.as_array
        
        return SimpleTile(base)
    
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
    def as_mask(self) -> "SimpleTile":
        """Returns the SimpleTile as a mask (only L channel).
        Useful to ensure a mask is indeed a mask.
        
        Returns:
            SimpleTile: The converted SimpleTile.
        """
        
        return SimpleTile(self.image.convert('L'))
    
    @property
    def as_array(self) -> np.typing.NDArray:
        """Returns the SimpleTile as a numpy array.
        Useful for matrix operations.
        
        Returns:
            np.ndarray: The numpy array.
        """
        
        return np.array(self.image)
    
    @property
    def copy(self) -> "SimpleTile":
        return SimpleTile(self.image.copy())
    
    # def scale(self, factor: float, how = None) -> "Tile":
    #     how = how if how is not None else Image.Resampling.NEAREST
    #     return Tile.from_image(ImageOps.scale(self.image, factor, how))
    
    def display(self, factor: float = 1.0, how: Image.Resampling = Image.Resampling.NEAREST) -> None:
        display(ImageOps.scale(self.image, factor, how))
    
    def rotate(self, degrees: int, expand: bool = True) -> "SimpleTile":
        self.image = self.image.rotate(degrees, expand=True)
        
        return self
    
    def mirror(self, how: Literal['|', '-', '/', '\\']) -> "SimpleTile":
        """Mirrors the SimpleTile in the horizontal, vertical or diagonal directions.  
        
        Args:
            how ('-', '|', '/', '\\'): Which axis to mirror the image.
        
        Returns:
            Tile: The mirrored Tile.
        """
        
        match how:
            case '-':
                self.image = ImageOps.flip(self.image)
            
            case '|':
                self.image = ImageOps.mirror(self.image)
            
            case '\\':
                self.image = self.image.transpose(Image.Transpose.TRANSPOSE)
            
            case '/':
                self.image = self.image.transpose(Image.Transpose.TRANSVERSE)
        
        return self
    
    def scale(self, factor: float, how = None) -> "SimpleTile":
        how = how if how is not None else Image.Resampling.NEAREST
        self.image = ImageOps.scale(self.image, factor, how)
        
        return self
    
    def get_cutout(self, mask: "SimpleTile") -> "SimpleTile":
        image = self.image.copy()
        image.putalpha(mask.as_mask.image)
        return SimpleTile(image)
    
    def get_padout(self, fullsize: tuple[int, int], pos: tuple[int, int] = (0, 0)) -> "SimpleTile":
        image = Image.new(self.image.mode, fullsize, 0)
        image.paste(self.image, pos)
        return SimpleTile(image)
    
    def get_sample(self, box: tuple[int, int, int, int]) -> "SimpleTile":
        return SimpleTile(self.image.crop(box))
    
    def take(self, pos: tuple[int, int], size: tuple[int, int]) -> "SimpleTile":
        x0, y0 = pos
        width, height = size
        wrap_width, wrap_height = self.size
        
        xidx = (np.arange(x0, x0+width) % wrap_width)
        yidx = (np.arange(y0, y0+height) % wrap_height)
        
        crop = self.as_array[np.ix_(yidx, xidx)]
        
        return SimpleTile(crop)












class TileShape(Enum):
    UNKNOWN     = 0
    RECTANGULAR = 1
    ISOMETRIC   = 2
    HEXAGONAL   = 3

class TileType(Enum):
    UNKNOWN = 0
    DATA    = 1 # Can be BASE or HEAD
    MASK    = 2 # Greyscale 0-255
    
_TileShape = Literal['rect', 'iso', 'hex', None]
_TileType = Literal['data', 'mask', None]

# TODO: Add inplace options for methods

class Tile:
    """The base Tile class for tiling operations
    
    Returns:
        Tile: An image wrapped around tiling methods
    """
    
    def __init__(self,
            image: Image.Image,
            shape: _TileShape = None,
            ttype: _TileType = None,
        ) -> None:
        
        # image.mode -> "RGB" DATA | "L" MASK
        if ttype == 'data' and image.mode not in ('RBG', 'RBGA'):
            image = image.convert('RGB')
        
        elif ttype == 'mask' and image.mode != 'L':
            image = image.convert('L')
        
        self.image: Image.Image = image
        self.shape: _TileShape  = shape
        self.ttype: _TileType   = ttype
    
    @staticmethod
    def from_image(image: Image, shape: _TileShape = None, ttype: _TileType = None) -> "Tile":
        """Creates a Tile from an in-memory PIL Image.
        Useful for runtime created images.
        
        Args:
            image (Image): The PIL Image.
        
        Returns:
            Tile: The loaded Tile
        """
        
        return Tile(image, shape, ttype)
    
    @staticmethod
    def from_path(path: str, shape: _TileShape = None, ttype: _TileType = None) -> "Tile":
        """Creates a Tile from a locally stored image
        
        Args:
            path (str): The path to the image file, PNG or BMP.
        
        Returns:
            Tile: The loaded Tile
        """
        
        return Tile(Image.open(path), shape, ttype)
    
    @staticmethod
    def from_array(array: np.array, shape: _TileShape = None, ttype: _TileType = None) -> "Tile":
        """Creates a Tile from a numpy array.
        Useful for script generated data.
        
        Args:
            array (np.array): The numpy array with image info.
        
        Returns:
            Tile: The converted Tile.
        """
        
        return Tile(Image.fromarray(array), shape, ttype)
    
    @property
    def as_mask(self) -> "Tile":
        """Returns the Tile as a mask (only one channel).
        Useful to ensure a mask is indeed a mask.
        
        Returns:
            Tile: The converted Tile.
        """
        
        return Tile.from_image(self.image, self.shape, 'mask')
    
    @property
    def as_array(self) -> np.ndarray:
        """Returns the Tile as a numpy array.
        Useful for matrix operations.
        
        Returns:
            np.ndarray: The numpy array.
        """
        
        return np.array(self.image)
    
    @staticmethod
    def merge(base: "Tile", head: "Tile", mask: "Tile" = None, alpha: float = 0.5) -> "Tile":
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
        
        else:
            image = Image.composite(base.image, head.image, mask.as_mask.image)
        
        return Tile.from_image(image, base.shape, 'data')
    
    @staticmethod
    def merge_masks(*masks: "Tile") -> "Tile":
        """Adds several MASKs together.
        Their values are combined with bitwise OR.
        
        Returns:
            Tile: A single Tile MASK
        """
        
        assert len(masks) >= 2, "Insufficient masks to be merged (<2)"
        
        base = masks[0].as_array
        
        for mask in masks[1:]:
            base |= mask.as_array
        
        return Tile.from_array(base)
    
    def rotate(self, degrees: int) -> "Tile":
        """Rotates the Tile by 45 or 90 degree angles.
        If used with 45 angles, lossy converts rectangular to isometric.
        
        Args:
            degrees (int): The angle in degrees ??? clockwise ??? # FIXME check direction
        
        Returns:
            Tile: The rotated Tile
        """
        
        if degrees % 90 == 0:
            image = self.image.rotate(degrees)
        
        elif degrees % 45 == 0:
            wdt, hgt = self.image.size
            image = self.image.rotate(degrees, expand=True).resize((wdt*2, hgt))
            # image = image.crop((1, 0, 2*wdt-1, hgt))
        
        else:
            image = self.image
        
        return Tile.from_image(image, self.shape, self.ttype)
    
    def mirror(self, how: Literal["|", "-"]) -> "Tile":
        """Mirrors the Tile in the horizontal or vertical direction.  
        
        ```
        Horizontal ('-'):
        |1 v 2|    |3   4|
        |-----| -> |     |
        |3 ^ 4|    |1   2|
        
        Vertical ('|'):
        |1 | 2|    |2   1|
        | >|< | -> |     |
        |3 | 4|    |4   3|
        ```
        
        Args:
            how ('-' or '|'): Which axis to mirror the image.
        
        Returns:
            Tile: The mirrored Tile.
        """
        
        if how == "|":
            image = ImageOps.mirror(self.image)
        
        if how == "-":
            image = ImageOps.flip(self.image)
        
        return Tile.from_image(image)
    
    def scale(self, factor: float, how = None) -> "Tile":
        how = how if how is not None else Image.Resampling.NEAREST
        return Tile.from_image(ImageOps.scale(self.image, factor, how))
    
    def cut(self, mask: "Tile") -> "Tile":
        pass
    
    def display(self, scale: float = 1.0, how = None) -> None:
        display(self.scale(scale, how).image)




























