

# Tile Shapes

There are three basic shapes of tiles:

## Square
![[sample_tile_square_24.png]]

## Isometric
![[sample_tile_iso_24.png]]

## Hexagonal
Horizontal (flat)
![[sample_tile_hex_flat_24.png]]

Vertical (point).
![[sample_tile_hex_point_24.png]]  



# Tile Ordering

Every tile is centered on itself, and is indexed as 0.

The first reference tile is the topmost + leftmost tile.
All the others follow a clockwise sequence around the center tile:

For square tiles
![[square_order.png]]

For isometric tiles
![[iso_order.png]]

The isometric tile can be seen as a skewed -45º rotation of the square tile.
This helps creating a single simplified algorithm for both of them.


For horizontal hexagonal tiles
![[hex_flat_order.png]]

For vertical hexagonal tiles
![[hex_point_order.png]]

Tile ordering matters when calculating mask merging for border interaction.



# Tile Purpose

A tile is always a PNG image, and can be one of three types.

## Base | Head
Both contain the same type of information.
However, the Base goes on the bottom and the Head goes on top.
## Mask
A special tile used to combine a BASE with a HEAD.
It must have the same dimensions as the BASE and HEAD.
It's a grey scale with values ranging from 0 (full BASE) to 255 (full HEAD).























