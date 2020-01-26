from pyglet.gl import *
import math
import random
from everett.worldgraph import world
from everett.worldgenerators import world_three

world = world_three.generate_world(seed=random.randint(1,1000), total_cells_desired=10001)

window = pyglet.window.Window()

planet_centre_coord = [window.width/2, window.height/2, 0]
planet_drawn_radius = window.height/3

def random_c3B_colour():
    return [random.randint(0,255),random.randint(0,255), random.randint(0,255)]

# Construct circle
circle_sides = 50
blue_planet_vertex_list = pyglet.graphics.vertex_list(circle_sides+2, 'v2f', 'c3B')
blue_planet_vertex_list.vertices[:2] = planet_centre_coord[:2]
for p in range(circle_sides):
    blue_planet_vertex_list.vertices[2*(p+1):2*(p+2)] = [planet_centre_coord[0] + (planet_drawn_radius * math.sin((p/circle_sides)*2*math.pi)),
                                                         planet_centre_coord[1] + (planet_drawn_radius * math.cos((p/circle_sides)*2*math.pi))]
blue_planet_vertex_list.vertices[-2:] = [planet_centre_coord[0] + (planet_drawn_radius * math.sin(2*math.pi)),
                                         planet_centre_coord[1] + (planet_drawn_radius * math.cos(2*math.pi))]

blue_planet_vertex_list.colors[:] = [0, 0, 255]* (len(blue_planet_vertex_list.vertices)//2)

# Construct worldgraph verts
all_land_verts = list()
land_sizes = list()
# Each land is a list of node ids for a contiguous set of land nodes
cartesian_locs = world.node_manager.cartesian_locs # make local
for land in world.lands:
    next_land_verts = list()
    for node_id in land:
        p = cartesian_locs[node_id]
        next_land_vert = [planet_centre_coord[0]+(p[0]*planet_drawn_radius),
                          planet_centre_coord[1]+(p[1]*planet_drawn_radius),
                          planet_centre_coord[2]+(p[2]*planet_drawn_radius)]
        if next_land_vert[2] >= 0: # Omit points on other side of world
            next_land_verts.extend([next_land_vert[0], next_land_vert[1], 0]) # Draw Z at origin
    all_land_verts.extend(next_land_verts)
    # Remember land size so it can be coloured
    land_sizes.append(len(next_land_verts)//3)
total_land_verts = len(all_land_verts) // 3
worldgraph_vertex_list = pyglet.graphics.vertex_list(total_land_verts, 'v3f', 'c3B')
worldgraph_vertex_list.vertices[:] = all_land_verts
colours = list()
for land_size in land_sizes:
    colours.extend(random_c3B_colour() * land_size)
worldgraph_vertex_list.colors[:] = colours


@window.event
def on_draw():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    #glDrawArrays(GL_TRIANGLES, 0, len(vertices) // 2)
    #blue_planet_vertex_list.draw(pyglet.gl.GL_TRIANGLE_FAN)
    worldgraph_vertex_list.draw(pyglet.gl.GL_POINTS)

pyglet.app.run()
