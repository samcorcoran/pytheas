import math

from pyglet.gl import *
from everett.worldgraph import world
from everett.worldgenerators import world_three
from everett.spherepoints.cartesian_utils import geographic_location_to_cartesian_point
from everett.spherepoints.geographic_utils import Location
from everett.spherepoints.vector_utils import normalized, magnitude
import pytheas_config as config

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
    world = world_three.generate_world(seed=954, total_cells_desired=config.number_of_cells)

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
def construct_node_verts_with_boundary_duplicates():
    """ Populate verts and node-id-to-index mapping in centre_node_id_to_boundary_vert_idx_list """
    nm = world.node_manager
    verts = list()
    num_verts = 0
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
    return verts, num_verts


@print_timer
def construct_2d_node_verts_with_boundary_duplicates(longitude_offset_for_rotation):
    """
    Retrieve node geographic data and create 2d vertex positions, adjusting to place boundary points on the same side of
    the map as the cell's centre node.

    Modify node lon,lat based on globe rotation (offsetting where origin is) or any wrapping needs to draw cells all on one
    side of the map or the other (rather than incorrectly spanning entire map width).

    longitudeOffset: Degrees globe is rotated around z axis (globe's North South polar axis) from its default position
    """
    nm = world.node_manager
    verts_2d = list()
    num_verts_2d = 0
    for i, node_id in enumerate(nm.cells):
        # Add centre node to list
        centre_geographic_loc = nm.geographic_locs[node_id]
        # Apply rotational offset to longitude value
        centre_lon = clamp_to_longitude_range(centre_geographic_loc.longitude + longitude_offset_for_rotation)
        centre_geographic_loc = Location(centre_lon, centre_geographic_loc.latitude)
        centre_point = geographic_to_2d_cartesian(centre_geographic_loc, False, None)
        verts_2d.extend(centre_point)
        # Store index in vert
        node_ids_to_vert_idx[node_id] = num_verts_2d
        num_verts_2d += 1

        # Determine if east or west
        centre_is_eastern = centre_geographic_loc.longitude > 0
        # TODO: Is there a need for is_northern? Hexes that wrap over the pole should go higher than the top of the map

        # Now add its boundary points
        centre_node_id_to_boundary_vert_idx_list[node_id] = list()
        for bp_id in nm.get_boundary_nodes_of(node_id):
            bp_lon, bp_lat = nm.geographic_locs[bp_id]
            bp_lon += longitude_offset_for_rotation
            verts_2d.extend(geographic_to_2d_cartesian(Location(bp_lon, bp_lat), is_boundary_point=True, centre_is_eastern=centre_is_eastern))

            # Remember the id's direct mapping to verts
            node_ids_to_vert_idx[node_id] = num_verts_2d

            # Also remember via which node was the centre
            centre_node_id_to_boundary_vert_idx_list[node_id].append(num_verts_2d)
            num_verts_2d += 1
    return verts_2d, num_verts_2d


def clamp_to_longitude_range(lon):
    if lon <= -180:
        lon = (lon % 360) + 360
    elif lon > 180:
        lon = (lon % 360) - 360
    return lon


# TODO: Rename this to something less generic and more specific to cell centre and boundary locations
def geographic_to_2d_cartesian(geo_loc, is_boundary_point, centre_is_eastern):
    y = 0 # Fixed depth for placing the 2d map in space
    # East-West dimensions
    x = geo_loc.longitude
    # Only boundary points are fixed for wrapping issues (side of map is dictated by cell centre's position)
    if is_boundary_point:
        if centre_is_eastern:
            if x < -90:
                ##print("Switching western Bp to east")
                # TODO: FIX THIS ASSUMPTION - it does not hold near poles, as 90 degrees covers a shorter distance and eventually is less than a cell radius
                # TODO: One option would be to retrieve bp positions relative to centre position rather than absolute positions
                # This boundary point is in the western hemisphere.
                # Assuming centre-point to boundary point is less than 90 degrees, this cell must straddle...
                # the back-seam of the globe's coordinate system.
                # Solution: Shift western bp to east of cell centre.
                x = x + 360
        else:
            # Therefore cell centre is western...
            if x > 90:
                ##print("Switching eastern Bp to west")
                # Boundary point is in eastern hemi, while cell centre is in western
                # Assuming cell radius is less than 90 degrees, this cell straddles.
                # Solution: Shift eastern bp to west of cell centre
                x = x - 360
    # Scale x to a smaller range, and flip it to match globe
    x = x / 100 * -1
    # North-South dimensions
    z = geo_loc.latitude
    # Scale [-90,90] to a smaller range
    z = z / 100
    return [x, y, z]


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
        for j in range(len(boundary_node_indices)):
            cell_triangle_idxs.append(cell_centre_vert_idx)
            cell_triangle_idxs.append(boundary_node_indices[j-1])
            cell_triangle_idxs.append(boundary_node_indices[j])
    return cell_triangle_idxs


def construct_3d_paths(batch_paths):
    path_verts = list()
    path_num_verts = 0
    path_indices = list()
    path_vert_colours = list()

    if config.render_river_paths:
        construct_river_paths(batch_paths)
    if config.render_cell_boundaries:
        construct_cell_boundary_paths(batch_paths)
    if construct_dummy_paths(batch_paths):
        config.render_dummy_paths

    return path_verts, path_num_verts, path_indices, path_vert_colours


def construct_river_paths(batch_paths):
    # Iterate over rivers, adding vert pairs for each segment
    nm = world.node_manager
    path_verts = list()
    path_vert_colours = list()
    for j, river in enumerate(nm.rivers):
        river_verts = list()
        for i, river_loc in enumerate(river.sequence_of_locs):
            river_point = geographic_location_to_cartesian_point(river_loc)
            river_verts.extend(river_point)
            # Double-add mid-river verts to serve as end and start of successive river segments
            if i != 0 and i != len(river.sequence_of_locs)-1:
                river_verts.extend(geographic_location_to_cartesian_point(river_loc))
        # Should now have pairs of verts in river_verts
        if len(river_verts)%2 != 0:
            print("WARNING: River with non-even number of vertices is going to mess up the line rendering. Ignored.")
            continue
        path_vert_colours.extend(cell_colouring.river_colour * (len(river_verts)//3))
        path_verts.extend(river_verts)
    num_path_verts = len(path_verts)//3
    batch_paths.add(num_path_verts, pyglet.gl.GL_LINES, None, ('v3f', path_verts), ('c3B', path_vert_colours))


def construct_dummy_paths(batch_paths):
    path_verts = list()
    path_vert_colours = list()
    path_verts.extend([1, 1, 1])
    path_vert_colours.extend([0, 255, 0])
    path_verts.extend([-1, 1, 1])
    path_vert_colours.extend([0, 255, 0])
    batch_paths.add(2, pyglet.gl.GL_LINES, None, ('v3f', path_verts), ('c3B', path_vert_colours))


def construct_dummy_linestrip_paths(path_verts, path_num_verts, path_indices, path_vert_colours):
    # Add a point at the origin to fix strange issue where an origin vertex seems to exist by default
    path_verts.extend([1, -1, 1])
    path_num_verts += 1
    path_indices.append(path_num_verts)
    path_indices.append(path_num_verts)
    path_vert_colours.extend([0, 255, 0])

    # First line
    path_verts.extend([1, 1, 1])
    path_num_verts += 1
    path_indices.append(path_num_verts)
    path_vert_colours.extend([0, 255, 0])

    path_verts.extend([-1, 1, 1])
    path_num_verts += 1
    path_indices.append(path_num_verts)
    path_indices.append(path_num_verts)
    path_vert_colours.extend([0, 255, 0])

    # Second line
    # #path_verts.extend(geographic_location_to_cartesian_point(Location(25, -25)))
    # path_verts.extend([-0.1, -2, 2])
    # path_num_verts += 1
    # path_indices.append(path_num_verts)
    # #path_verts.extend(geographic_location_to_cartesian_point(Location(-10, -45)))
    # path_verts.extend([-0.4, -0.4, 0.4])
    # path_num_verts += 1
    # path_indices.append(path_num_verts)

    return path_num_verts


def construct_cell_boundary_paths(batch_paths):
    nm = world.node_manager
    all_path_verts = list()
    all_path_colours = list()
    for j, cell_id in enumerate(world.node_manager.cells):
        path_verts = list()
        num_bps = 0
        for i, bp_id in enumerate(nm.get_boundary_nodes_of(cell_id)):
            path_verts.extend(nm.cartesian_locs[bp_id])
            # Double add for end of first line and start of next
            if i != 0:
                path_verts.extend(nm.cartesian_locs[bp_id])
            num_bps += 1
        first_vert = path_verts[0:3]
        path_verts.extend(first_vert)
        all_path_verts.extend(path_verts)

        num_verts = len(path_verts)//3
        path_colours = cell_colouring.cell_outline_colour*num_verts

        all_path_colours.extend(path_colours)
    batch_paths.add(len(all_path_verts)//3, pyglet.gl.GL_LINES, None, ('v3f', all_path_verts), ('c3B', all_path_colours))


def construct_blue_colour_list(num_verts):
    return cell_colouring.ocean_colour * num_verts

def construct_random_colour_list(num_verts):
    vert_colours = list()
    for n in range(num_verts):
        vert_colours.extend(cell_colouring.random_c3B_colour())
    return vert_colours