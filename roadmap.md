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


# List of Nice Values

| POW(2) | Dozens | Tenners |
|--------|--------|---------|
| 4      | 6      |         |
| 8      | 12     |         |
| 16     | 24     |         |
| 32     | 48     |         |
| 64     |        | 80      |
|        | 96     | 120     |
| 128    |        | 160     |
|        | 192    | 240     |
| 256    |        | 360     |
|        | 386    | 400     |
| 512    |        |         |