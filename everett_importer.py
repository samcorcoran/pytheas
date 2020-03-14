from pyglet.gl import *
import math
import random
from everett.worldgraph import world
from everett.worldgenerators import world_three

world = None

planet_centre_coord = [0,0]
planet_drawn_radius = 10

node_ids_to_vert_idx = dict()
centre_node_id_to_boundary_vert_idx_list = dict()

def generate_world():
    global world
    world = world_three.generate_world(seed=954, total_cells_desired=40000)

def random_c3B_colour():
    return [random.randint(0,255), random.randint(0,255), random.randint(0,255)]

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

def construct_node_verts_with_boundary_duplicates(num_verts, verts):
    nm = world.node_manager
    for i, node_id in enumerate(nm.cells):
        # Add centre node to list
        verts.extend(nm.cartesian_locs[node_id])
        # Store index in vert
        node_ids_to_vert_idx[node_id] = num_verts
        num_verts += 1
        # Now add its boundary points
        centre_node_id_to_boundary_vert_idx_list[node_id] = list()
        for bp_id in nm.get_boundary_nodes_of(node_id):
            verts.extend(nm.cartesian_locs[bp_id])
            # Remember the id's direct mapping to verts
            node_ids_to_vert_idx[node_id] = num_verts
            # Also remember via which node was the centre
            centre_node_id_to_boundary_vert_idx_list[node_id].append(num_verts)
            num_verts += 1
    return num_verts

def construct_node_verts(num_verts, verts):
    nm = world.node_manager
    for i, node_id in enumerate(nm.cells):
        # Add node to list
        verts.extend(nm.cartesian_locs[node_id])
        # Store index in vert
        node_ids_to_vert_idx[node_id] = num_verts
        num_verts += 1
    for i, node_id in enumerate(nm.all_boundary_nodes):
        # Add node to list
        verts.extend(nm.cartesian_locs[node_id])
        # Store index in vert
        node_ids_to_vert_idx[node_id] = num_verts
        num_verts += 1
    return num_verts

def construct_blue_colour_list(num_verts):
    return [20, 20, 80] * num_verts

def construct_random_colour_list(num_verts):
    vert_colours = list()
    for n in range(num_verts):
        vert_colours.extend(random_c3B_colour())
    return vert_colours

def construct_cell_indices():
    nm = world.node_manager
    cell_triangle_idxs = list()
    for i, cell_id in enumerate(nm.cells):
        cell_centre_vert_idx = node_ids_to_vert_idx[cell_id]
        # Convert everett node_ids to pytheas rendering indices
        boundary_node_indices = centre_node_id_to_boundary_vert_idx_list[cell_id]
        # Add a triplet of indices for each triangle segment (i.e. per boundary point)
        for i in range(len(boundary_node_indices)):
            cell_triangle_idxs.append(cell_centre_vert_idx)
            cell_triangle_idxs.append(boundary_node_indices[i-1])
            cell_triangle_idxs.append(boundary_node_indices[i])
    return cell_triangle_idxs

def update_cells_with_land_colours(indexed_vertex_list):
    nm = world.node_manager
    land_colour = [70, 160, 20]
    for n, cell_centre_id in enumerate(nm.land_node_ids):
        update_cell_with_colour(indexed_vertex_list, cell_centre_id, land_colour)

def update_cell_with_colour(indexed_vertex_list, center_node_id, colour):
    centre_idx = node_ids_to_vert_idx[center_node_id]
    start = centre_idx * 3
    end = start + 3
    indexed_vertex_list.colors[start:end] = colour
    for bp_idx in centre_node_id_to_boundary_vert_idx_list[center_node_id]:
        start = bp_idx * 3
        end = start + 3
        indexed_vertex_list.colors[start:end] = colour

def update_cells_with_altitude_colours(indexed_vertex_list):
    from everett.features.featuretaxonomy import Feature
    nm = world.node_manager
    for n, cell_centre_id in enumerate(nm.land_node_ids):
        cell_value = nm.get_feature(cell_centre_id, Feature.terrain_altitude)/10000
        if cell_value >= 0:
            cell_colour = [0, 50 + int(205*cell_value), 0]
        else:
            # Colour land cells with negative altitudes blue
            cell_colour = [0, 0, int(255*(cell_value*-1))]
            # TODO: Figure out why some land cells have negative altitudes
            #cell_colour = [255, 0, 0]
        update_cell_with_colour(indexed_vertex_list, cell_centre_id, cell_colour)
