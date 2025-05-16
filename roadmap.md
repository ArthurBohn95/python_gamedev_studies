The studies should and follow:

- Images
  - pillow (PIL) vs opencv (cv2)
    - Opening images
    - Manipulating images
    - Generating images
  
  - Tiles
    - Defining tiles shapes
    - Defining tiles types
    - Tile operations
      - Load in many ways
        - Tile.from_path, Tile.from_image, Tile.from_array
      - Export as image or game object
      - Generate from parameters
      - Merge with other tiles
      - Combine using masks
      - Apply mask for transparency
    
    - Tile manipulation
      - Flip
      - Mirror
      - Rotate
      - Scale
      - Invert (mask)
      - Cut (mask)
      - Fill (template)
      - Mask
    
    - Tile generation
      - Wireframe
      - Filling
      - Cutting
      - Sampling
    
    - Border interaction algorithm
    - Chunking and optimization


# Tile Naming Convention

## `D` for Data:
- `T` for Texture
- `M` for Mask
  - len 8 for Orthogonal and Isometric, 6 for Hexagonals
  - '0' for base
  - '1' for head
  - 'x' for any

## `S` for Shape:
- `O` for Orthogonal
- `I` for Isometric
- `HP` for Hexagonal Point
- `HF` for Hexagonal Flat

## `R` for Rotation:
- `X` for None (0 only)
- `H` for Half (0, 180)
- `F` for Full (0, 90, 180, 270)

## `O` for Orientation
- `X` for None (fixed)
- `H` for Horizontal (left-right)
- `V` for Vertical (top-bottom)
- `A` for Any


# List of Nice Values

| 2<sup>n</sup> | 2<sup>n</sup>x1.5 | 10n |
|--------|--------|---------|
| 4      | 6      |         |
| 8      | 12     |         |
| 16     | 24     |         |
| 32     | 48     |         |
| 64     |        | 80      |
|        | 96     | 120     |
| 128    |        | 160     |
|        | 192    | 240     |
| 256    |        | 320     |
|        |        | 360     |
|        | 384    | 400     |
| 512    |        | 640     |
|        |        | 720     |
|        | 768    | 800     |
|        |        | 960     |
| 1024   |        | 1080    |

# List of Nice Resolutions

| Resolution | Aspect<br>Ratio | Notes                     |
|------------|-----------------|---------------------------|
| 256x192    | 16:9            |                           |
| 320x180    | 16:9            | 6xFHD                     |
| 320x240    | 4:3             | Classic Retro             |
| 384x240    | 16:10           | 240p                      |
| 480x270    | 16:9            | 4xFHD                     |
| 640x360    | 16:9            | 2xHD<br>3xFHD<br>4xQHD    |
| 640x480    | 4:3             | VGA Standard              |
| 768x480    | 16:10           |  |
