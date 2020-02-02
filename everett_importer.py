from pyglet.gl import *
import math
import random
from everett.worldgraph import world
from everett.worldgenerators import world_three

#world = world_three.generate_world(seed=random.randint(1,1000), total_cells_desired=1000)
world = world_three.generate_world(seed=954, total_cells_desired=1000)

planet_centre_coord = [0,0]
planet_drawn_radius = 10

id_to_vertex_idx = dict()

def random_c3B_colour():
    return [random.randint(0,255),random.randint(0,255), random.randint(0,255)]

def colour_generator(num_colours):
    # Generates debug colours (stronger red for each successively)
    frac = 255//(num_colours+2)
    for n in range(num_colours):
        yield [(frac*2)+(frac*(n+1)), 0, 0]

def land_verts():
    # Construct worldgraph verts
    all_land_verts = list()
    land_sizes = list()
    # Each land is a list of node ids for a contiguous set of land nodes
    cartesian_locs = world.node_manager.cartesian_locs # make local
    for land in world.lands:
        next_land_verts = list()
        for node_id in land:
            p = cartesian_locs[node_id]
            next_land_verts.extend(p)
        all_land_verts.extend(next_land_verts)
        # Remember land size so it can be coloured
        land_sizes.append(len(next_land_verts)//3)
    return all_land_verts, land_sizes

def construct_worldgraph_verts(worldgraph_vertex_list):
    all_land_verts, land_sizes = land_verts()
    total_land_verts = len(all_land_verts) // 3
    worldgraph_vertex_list.resize(total_land_verts)
    worldgraph_vertex_list.vertices[:] = all_land_verts
    colours = list()
    for land_size in land_sizes:
        colours.extend(random_c3B_colour() * land_size)
    worldgraph_vertex_list.colors[:] = colours

def construct_cell_vertex_list(cell_vertex_list, cell_bp_nums):
    all_land_cell_verts = list()
    land_cell_colours = list()
    for n, cell_id in enumerate(world.node_manager.all_centre_nodes):
        cell_verts = []

        cell_centre_point = world.node_manager.cartesian_locs[cell_id]
        bps = list(world.node_manager.boundary_nodes[cell_id])
        for i, bp in enumerate(bps):
            cell_verts.extend(cell_centre_point)
            cell_verts.extend(world.node_manager.cartesian_locs[bps[i-1]])
            cell_verts.extend(world.node_manager.cartesian_locs[bps[i]])

        cols = [0, 0, 240] * (len(cell_verts)//3) # All blue
        #cols = random_c3B_colour() * (len(cell_verts)//3) # Random colour
        land_cell_colours.extend(cols)
        all_land_cell_verts.extend(cell_verts)

        id_to_vertex_idx[cell_id] = len(all_land_cell_verts)
        cell_bp_nums[cell_id] = len(bps)+1

    # Copy vertex information into pyglet vertex_list
    num_verts = len(all_land_cell_verts)//3
    cell_vertex_list.resize(num_verts)
    cell_vertex_list.vertices[:] = all_land_cell_verts
    cell_vertex_list.colors[:] = land_cell_colours

def update_cells_with_land_colours(cell_vertex_list, cell_bp_nums):
    for n, cell_id in enumerate(world.node_manager.land_node_ids):
        start = id_to_vertex_idx[cell_id]
        total_verts = cell_bp_nums[cell_id]
        end = start + total_verts*3
        cell_vertex_list.colors[start:end] = [0, 210, 0]*total_verts