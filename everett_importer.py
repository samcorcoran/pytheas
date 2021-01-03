from pyglet.gl import *
from everett.worldgraph import world
from everett.worldgenerators import world_three

import cell_colouring
from print_timer import print_timer


world = None

def world_node_manager():
    return world.node_manager

planet_centre_coord = [0,0]
planet_drawn_radius = 10

node_ids_to_vert_idx = dict()
centre_node_id_to_boundary_vert_idx_list = dict()

@print_timer
def generate_world():
    global world
    world = world_three.generate_world(seed=954, total_cells_desired=1000)

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
#TODO: Remove this unused land-only function?
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

def construct_2d_node_verts_with_boundary_duplicates(num_verts, verts_2d):
    """
    Retrieve node data and map geographic data and create 2d vertex positions

    Determine
    """
    nm = world.node_manager
    for i, node_id in enumerate(nm.cells):
        # Add centre node to list
        centre_geographic_loc = nm.geographic_locs[node_id]
        verts_2d.extend(geographic_to_2d_cartesian(centre_geographic_loc, False))
        # Store index in vert
        node_ids_to_vert_idx[node_id] = num_verts
        num_verts += 1

        # Determine if east or west
        centre_is_eastern = centre_geographic_loc[0] > 0
        # TODO: Is there a need for is_northern? Hexes that wrap over the pole should go higher than the top of the map

        is_eastern_flags = []
        bp_geo_locs = list()
        for bp_id in nm.get_boundary_nodes_of(node_id):
            bp_geo_loc = nm.geographic_locs[bp_id]
            if centre_is_eastern:
                if bp_geo_loc[0] < -90:
                    # TODO: FIX THIS ASSUMPTION - it does not hold near poles, as 90 degrees covers a shorter distance and eventually is less th
                    # This boundary point is in the western hemisphere.
                    # Assuming centre-point to boundary point is less than 90 degrees, this cell must straddle...
                    # the back-seam of the globe's coordinate system.
                    # Solution: Shift western bp to east of cell centre.
                    bp_geo_locs.append([bp_geo_loc[0] + 360, bp_geo_loc[1]])
            else:
                if bp_geo_loc[0] > 90:
                    # Boundary point is in eastern hemi, while cell centre is in western
                    # Assuming cell radius is less than 90 degrees, this cell straddles.
                    # Solution: Shift eastern bp to west of cell centre
                    bp_geo_locs.append([bp_geo_loc[0] - 360, bp_geo_loc[1]])

        # Now add its boundary points
        centre_node_id_to_boundary_vert_idx_list[node_id] = list()
        for bp_id in nm.get_boundary_nodes_of(node_id):
            bp_geographic_loc = nm.geographic_locs[bp_id]
            verts_2d.extend(geographic_to_2d_cartesian(bp_geographic_loc, centre_is_eastern))

            # Remember the id's direct mapping to verts
            node_ids_to_vert_idx[node_id] = num_verts

            # Also remember via which node was the centre
            centre_node_id_to_boundary_vert_idx_list[node_id].append(num_verts)
            num_verts += 1
    return num_verts

def geographic_to_2d_cartesian(geo_loc, centre_is_eastern):
    y = 0 # Fixed depth for placing the 2d map in space
    # East-West dimensions
    x = geo_loc[0]
    # Scale [-180,180] to a smaller range
    x = x / 100
    # North-South dimensions
    z = geo_loc[1]
    # Scale [-90,90] to a smaller range
    z = z / 100
    return [x, y, z]

@print_timer
def construct_dummy_nodes(num_verts, verts):
    """ Construct one face of a half-size cube with two triangles, for debug """
    x1 = [-0.5, -0.5, 0]
    x2 = [0.5, -0.5, 0]
    x3 = [-0.5, 0.5, 0]
    x4 = [0.5, 0.5, 0]
    verts.extend(x1)
    verts.extend(x2)
    verts.extend(x3)
    verts.extend(x2)
    verts.extend(x3)
    verts.extend(x4)
    num_verts = 6
    node_ids_to_vert_idx[1] = 0
    node_ids_to_vert_idx[2] = 1
    node_ids_to_vert_idx[3] = 2
    node_ids_to_vert_idx[4] = 1
    node_ids_to_vert_idx[5] = 2
    node_ids_to_vert_idx[6] = 3
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

def construct_dummy_cell_indices():
    cell_triangle_idxs = [0, 1, 2, 3, 4, 5]
    return cell_triangle_idxs

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

def convert_to_flat_verts(verts, num_verts):
    nm = world.node_manager
    print("lengths")
    print(len(verts))
    print(num_verts)
    flat_verts = [0.0, 0.0, 0.0] * num_verts

    #for x in range(len(verts)):
        #flat_verts[x] = verts[x]

    temp_populate_flat_verts(flat_verts)
    ###temp_populate_flat_verts_for_dummy(flat_verts)

    return flat_verts

def temp_populate_flat_verts(flat_verts):
    nm = world.node_manager
    for centre_node_id in nm.cells:
        # Update position for centre node verts
        centre_vertex_idx = node_ids_to_vert_idx[centre_node_id]
        #print("CENTRE")
        #print("{0}, {1}, {2}".format(flat_verts[centre_vertex_idx], flat_verts[centre_vertex_idx+1], flat_verts[centre_vertex_idx+2]))
        flat_verts[centre_vertex_idx] = 1
        flat_verts[centre_vertex_idx+1] = -1
        flat_verts[centre_vertex_idx+2] = 0
        # Update positions for boundary node verts
        boundary_node_vert_idx_list = centre_node_id_to_boundary_vert_idx_list[centre_node_id]
        for i, boundary_node_id in enumerate(nm.get_boundary_nodes_of(centre_node_id)):
            b_vertex_index = boundary_node_vert_idx_list[i]
            flat_verts[b_vertex_index] = 1
            flat_verts[b_vertex_index+1] = -1
            flat_verts[b_vertex_index+2] = 0

def temp_populate_flat_verts_for_dummy(flat_verts):
    nm = world.node_manager
    for i in range(0, len(flat_verts), 3):
        if i % 3 == 0:
            flat_verts[i] = 1
            flat_verts[i+1] = -1
            flat_verts[i+2] = 0
        elif i % 3 == 1:
            flat_verts[i] = -1
            flat_verts[i+1] = 1
            flat_verts[i+2] = 0
        elif i % 3 == 2:
            flat_verts[i] = 1
            flat_verts[i+1] = 1
            flat_verts[i+2] = 0

def convert_to_flat_verts2(verts):
    # Get each cell's lonlat converted to xyz
    # Use cells id to get boundary ids
    # Use boundary ids to get lonlat converted to xyz
    nm = world.node_manager
    flat_verts = list(verts)
    j=0
    for centre_node_id in centre_node_id_to_boundary_vert_idx_list.keys():
        centre_vertex_idx = node_ids_to_vert_idx[centre_node_id]
        # Get centre lon/lat
        centre_lon = nm.get_longitude(centre_node_id)
        centre_lat = nm.get_latitude(centre_node_id)
        # Convert to 2d
        y = centre_lat / 90.0
        x = centre_lon / 180.0
        ##print("{0}, {1} becomes {2}. {3}, {4}".format(centre_lon, centre_lat, x, y, 0))
        # Update vertex information for id

        if j == 0:
            flat_verts[centre_vertex_idx] = x
            flat_verts[centre_vertex_idx+1] = y
            flat_verts[centre_vertex_idx+2] = 1
        else:
            flat_verts[centre_vertex_idx] = 0
            flat_verts[centre_vertex_idx+1] = 0
            flat_verts[centre_vertex_idx+2] = 0
        boundary_node_vert_idx_list = centre_node_id_to_boundary_vert_idx_list[centre_node_id]
        for i, boundary_node_id in enumerate(nm.get_boundary_nodes_of(centre_node_id)):
            if j == 0:
                ##print("Boundary node id: {0}".format(boundary_node_id))
                pass

            b_lon = nm.get_longitude(boundary_node_id)
            b_lat = nm.get_latitude(boundary_node_id)
            b_y = b_lat / 90.0
            b_x = b_lon / 180.0
            ##print("{0}, {1} becomes {2}. {3}, {4}".format(b_lon, b_lat, b_x, b_y, 0))
            #if b_x < 0 and x > 0:
            #    b_x += 1
            #elif b_x > 0 and x < 0:
            #    b_x -= 1
            b_vert_idx = boundary_node_vert_idx_list[i]

            # First cell, first 66 boundary ids i < 66
            if j == 0:
                flat_verts[b_vert_idx] = b_x
                flat_verts[b_vert_idx+1] = b_y
                flat_verts[b_vert_idx+2] = 0
            else:
                flat_verts[centre_vertex_idx] = 0
                flat_verts[centre_vertex_idx+1] = 0
                flat_verts[centre_vertex_idx+2] = 0
        j += 1

    return flat_verts
