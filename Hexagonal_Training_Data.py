#%%
import collections
import math
from PIL import Image, ImageDraw, ImageFont

#%%
#Defining functions of hexogonal grid
Point = collections.namedtuple("Point", ["x", "y"])


_Hex = collections.namedtuple("Hex", ["q", "r", "s"])

def Hex(q, r, s): #creates the hexagon datatype 
    assert not (round(q + r + s) != 0), "q + r + s must be 0"
    return _Hex(q, r, s)

def eq(a,b): #Returns wether or not two hexs are equal
    return a.q==b.q and a.r==b.r and a.s==b.s

#Vector operators for hexagons
def hex_add(a, b): 
    return Hex(a.q + b.q, a.r + b.r, a.s + b.s)

def hex_subtract(a, b):
    return Hex(a.q - b.q, a.r - b.r, a.s - b.s)

def hex_scale(a, k:int):
    return Hex(a.q * k, a.r * k, a.s * k)

def hex_rotate_left(a):
    return Hex(-a.s, -a.q, -a.r)

def hex_rotate_right(a):
    return Hex(-a.r, -a.s, -a.q)

def hex_flip_q(a):
    return Hex(-a.q,a.r,a.q-a.r)

def hex_flip_r(a):
    return Hex(a.q,-a.r,-a.q+a.r)

def hex_length(hex): #length of the line from 0,0 to the hexagon
    return (abs(hex.q) + abs(hex.r) + abs(hex.s)) // 2

def hex_distance(a, b): #distance between two hexagons
    return hex_length(hex_subtract(a, b))

#Functions to move directionly in the lattice or aquire neibhbors
hex_directions = [Hex(1, 0, -1), Hex(1, -1, 0), Hex(0, -1, 1), Hex(-1, 0, 1), Hex(-1, 1, 0), Hex(0, 1, -1)]
def hex_direction(direction):
    return hex_directions[direction]

def hex_neighbor(hex, direction):
    return hex_add(hex, hex_direction(direction))


# Datatypes for pointy top or flattop lattices
Orientation = collections.namedtuple("Orientation", ["f0", "f1", "f2", "f3", "b0", "b1", "b2", "b3", "start_angle"])

Layout = collections.namedtuple("Layout", ["orientation", "size", "origin"])

layout_pointy = Orientation(math.sqrt(3.0), math.sqrt(3.0) / 2.0, 0.0, 3.0 / 2.0, math.sqrt(3.0) / 3.0, -1.0 / 3.0, 0.0, 2.0 / 3.0, 0.5)
layout_flat = Orientation(3.0 / 2.0, 0.0, math.sqrt(3.0) / 2.0, math.sqrt(3.0), 2.0 / 3.0, 0.0, -1.0 / 3.0, math.sqrt(3.0) / 3.0, 0.0)


#Functions for locating points in xy coordinates
def hex_to_pixel(layout, h): #returns the x,y coordinate of the center of the hexagon
    M = layout.orientation
    x = (M.f0*h.q+M.f1*h.r)*layout.size.x
    y = (M.f2*h.q+M.f3*h.r)*layout.size.y
    return Point(x + layout.origin.x , y + layout.origin.y)


def hex_corner_offset(layout, corner): #Returns how far off each corner is from the center point
    M = layout.orientation
    size = layout.size
    angle = 2.0 * math.pi * (M.start_angle - corner) / 6.0
    return Point(size.x * math.cos(angle), size.y * math.sin(angle))

def polygon_corners(layout, h): #Creates an array of corners by applying the corner offset method to the center six times
    corners = []
    center = hex_to_pixel(layout, h)
    for i in range(0, 6):
        offset = hex_corner_offset(layout, i)
        corners.append(Point(center.x + offset.x, center.y + offset.y))
    return corners

def to_tuple(corners): # 
    tuple_corners=[]
    for p in corners:
        tuple_corners.append((p.x,p.y))
    return tuple_corners



# Creates rectangular map of hexagons, origin is in top left
def rect_map(map_height,map_width):
    map=[]
    for r in range(map_height):
        r_offset=math.floor(r/2)
        for q in range(-r_offset,map_width-r_offset):
            #map.append(Hex(q,r-map_height//2,-(q)-(r-map_height//2)))
            map.append(Hex(q,r,-q-r))
    return map


#%%
#Functions for drawing hexagons
def plot_hex_grid(h,draw):
    corners=to_tuple(polygon_corners(layout,h))
    draw.polygon(corners,outline='white')

def plot_hex_grid_text(h,draw):   #writes the q,r coordinates in the middle of each hexagon
    corners=to_tuple(polygon_corners(layout,h))
    draw.polygon(corners,outline='white')
    shift=d.textsize(f"({h.q},{h.r})")
    draw.text((hex_to_pixel(layout,h).x-shift[0]//2,hex_to_pixel(layout,h).y-shift[1]//2),f"({h.q},{h.r})",fill='white')

def plot_hex_dots(h,draw):
    corners=to_tuple(polygon_corners(layout,h))
    dot_size=70
    for p in corners:
        p1=(p[0]-dot_size,p[1]-dot_size)
        p2=(p[0]+dot_size,p[1]+dot_size)
        draw.ellipse([p1,p2],fill='white')




#%%
#Drawing Hexogonal grid
image_size=(10240,10240)
im=Image.new('1',image_size,color=0)
d=ImageDraw.Draw(im)
#origin=Point(image_size[0]//2,image_size[1]//2) #middle of the imgage
origin=Point(0,0) #Top left corner
size=Point(1500,1500)
layout= Layout(layout_pointy,size,origin)
map=rect_map(6,6)

for h in map:
    plot_hex_dots(h,d)
    
im.show()
im.save("hex_lat_dots.png")



#%%
#Test functions
def complain(name):
    print("FAIL {0}".format(name))
def equal_hex(name, a, b):
    if not (a.q == b.q and a.s == b.s and a.r == b.r):
        complain(name)
def equal_int(name, a, b):
    if not (a == b):
        complain(name)
def equal_hex_array(name, a, b):
    equal_int(name, len(a), len(b))
    for i in range(0, len(a)):
        equal_hex(name, a[i], b[i])
def test_hex_arithmetic():
    equal_hex("hex_add", Hex(4, -10, 6), hex_add(Hex(1, -3, 2), Hex(3, -7, 4)))
    equal_hex("hex_subtract", Hex(-2, 4, -2), hex_subtract(Hex(1, -3, 2), Hex(3, -7, 4)))
def test_hex_direction():
    equal_hex("hex_direction", Hex(0, -1, 1), hex_direction(2))
def test_hex_neighbor():
    equal_hex("hex_neighbor", Hex(1, -3, 2), hex_neighbor(Hex(1, -2, 1), 2))
def test_hex_distance():
    equal_int("hex_distance", 7, hex_distance(Hex(3, -7, 4), Hex(0, 0, 0)))
def test_all():
    test_hex_arithmetic()
    test_hex_direction()
    test_hex_neighbor()
    test_hex_distance()
test_all()

