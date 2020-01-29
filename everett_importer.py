from pyglet.gl import *
import math
import random
from everett.worldgraph import world
from everett.worldgenerators import world_three

world = world_three.generate_world(seed=random.randint(1,1000), total_cells_desired=10000)

planet_centre_coord = [0,0]
planet_drawn_radius = 10

def random_c3B_colour():
    return [random.randint(0,255),random.randint(0,255), random.randint(0,255)]

def construct_blue_circle(blue_planet_vertex_list):
    # Construct circle
    circle_sides = 50
    blue_planet_vertex_list.resize(circle_sides+2)
    blue_planet_vertex_list.vertices[:2] = planet_centre_coord[:2]
    for p in range(circle_sides):
        blue_planet_vertex_list.vertices[2*(p+1):2*(p+2)] = [planet_drawn_radius * math.sin((p/circle_sides)*2*math.pi),
                                                             planet_drawn_radius * math.cos((p/circle_sides)*2*math.pi)]
    blue_planet_vertex_list.vertices[-2:] = [planet_drawn_radius * math.sin(2*math.pi),
                                             planet_drawn_radius * math.cos(2*math.pi)]

    blue_planet_vertex_list.colors[:] = [25, 100, 200]* (len(blue_planet_vertex_list.vertices)//2)

def construct_worldgraph_verts(worldgraph_vertex_list):
    # Construct worldgraph verts
    all_land_verts = list()
    land_sizes = list()
    # Each land is a list of node ids for a contiguous set of land nodes
    cartesian_locs = world.node_manager.cartesian_locs # make local
    for land in world.lands:
        next_land_verts = list()
        for node_id in land:
            p = cartesian_locs[node_id]
            next_land_verts.extend([p[0]*planet_drawn_radius,
                                    p[1]*planet_drawn_radius,
                                    p[2]*planet_drawn_radius])
        all_land_verts.extend(next_land_verts)
        # Remember land size so it can be coloured
        land_sizes.append(len(next_land_verts)//3)
    total_land_verts = len(all_land_verts) // 3
    worldgraph_vertex_list.resize(total_land_verts)
    worldgraph_vertex_list.vertices[:] = all_land_verts
    colours = list()
    for land_size in land_sizes:
        colours.extend(random_c3B_colour() * land_size)
    worldgraph_vertex_list.colors[:] = colours
