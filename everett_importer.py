from pyglet.gl import *
from everett.worldgraph import world
from everett.worldgenerators import world_three

import cell_colouring
from print_timer import print_timer

world = None

planet_centre_coord = [0,0]
planet_drawn_radius = 10

node_ids_to_vert_idx = dict()
centre_node_id_to_boundary_vert_idx_list = dict()

@print_timer
def generate_world():
    global world
    world = world_three.generate_world(seed=954, total_cells_desired=50)

@print_timer
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

@print_timer
def construct_worldgraph_verts(worldgraph_vertex_list):
    all_land_verts, land_sizes = land_verts()
    total_land_verts = len(all_land_verts) // 3
    worldgraph_vertex_list.resize(total_land_verts)
    worldgraph_vertex_list.vertices[:] = all_land_verts
    colours = list()
    for land_size in land_sizes:
        colours.extend(cell_colouring.random_c3B_colour() * land_size)
    worldgraph_vertex_list.colors[:] = colours

@print_timer
def construct_node_verts_with_boundary_duplicates(num_verts, verts):
    """ Populate verts and node-id-to-index mapping in centre_node_id_to_boundary_vert_idx_list """
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

@print_timer
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

@print_timer
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

def construct_blue_colour_list(num_verts):
    return cell_colouring.ocean_colour * num_verts

def construct_random_colour_list(num_verts):
    vert_colours = list()
    for n in range(num_verts):
        vert_colours.extend(cell_colouring.random_c3B_colour())
    return vert_colours

    nm = world.node_manager



    nm = world.node_manager
