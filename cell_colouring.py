import random
import everett_importer

from print_timer import print_timer

ocean_colour = [20, 20, 80]
river_colour = [40, 80, 200]
land_colour = [70, 160, 20]
cell_outline_colour = [80, 65, 65]

def debug_colour_generator(num_colours):
    # Generates debug colours (stronger red for each successively)
    frac = 255//(num_colours+2)
    for n in range(num_colours):
        yield [(frac*2)+(frac*(n+1)), 0, 0]

def random_c3B_colour():
    return [random.randint(0,255), random.randint(0,255), random.randint(0,255)]

def update_cell_with_colour(indexed_vertex_list, center_node_id, colour=None):
    colour = random_c3B_colour() if colour is None else colour # Default colour is random choice
    centre_idx = everett_importer.node_ids_to_vert_idx[center_node_id]
    start = centre_idx * 3
    end = start + 3

    indexed_vertex_list.colors[start:end] = colour
    for bp_idx in everett_importer.centre_node_id_to_boundary_vert_idx_list[center_node_id]:
        start = bp_idx * 3
        end = start + 3
        indexed_vertex_list.colors[start:end] = colour

@print_timer
def update_all_cells_with_colour(indexed_vertex_list, colour=[255,255,255]):
    indexed_vertex_list.colors = colour * indexed_vertex_list.get_size()

@print_timer
def update_cells_with_temperature_colours(indexed_vertex_list, min_temp=-10, max_temp=30):
    from everett.features.featuretaxonomy import Feature
    nm = everett_importer.world.node_manager
    for n, cell_centre_id in enumerate(nm.cells):
        cell_value = nm.get_feature(cell_centre_id, Feature.surface_temperature)
        cell_value = (cell_value + (-1 * min_temp)) / (max_temp + (-1 * min_temp))
        cell_colour = [int(80*cell_value), int(50*cell_value), int(100*(1-cell_value))]
        update_cell_with_colour(indexed_vertex_list, cell_centre_id, cell_colour)


@print_timer
def update_land_cells_with_whittaker_colours(indexed_vertex_list):
    # Make oceans blue, as otherwise temperature colours may persist
    update_all_cells_to_ocean(indexed_vertex_list)

    from everett.features.featuretaxonomy import Feature
    nm = everett_importer.world.node_manager
    for n, cell_centre_id in enumerate(nm.land_node_ids):
        r = nm.get_feature(cell_centre_id, Feature.render_colour_red)
        g = nm.get_feature(cell_centre_id, Feature.render_colour_green)
        b = nm.get_feature(cell_centre_id, Feature.render_colour_blue)
        update_cell_with_colour(indexed_vertex_list, cell_centre_id, [r, g, b])


@print_timer
def update_land_cells_with_altitude_colours(indexed_vertex_list):
    # Make oceans blue, as otherwise temperature colours may persist
    update_all_cells_to_ocean(indexed_vertex_list)

    from everett.features.featuretaxonomy import Feature
    nm = everett_importer.world.node_manager
    for cell_centre_id in nm.land_node_ids:
        cell_value = nm.get_feature(cell_centre_id, Feature.terrain_altitude)/10000
        if cell_value >= 0:
            cell_colour = [0, 50 + int(205*cell_value), 0]
        else:
            # Colour land cells with negative altitudes blue
            cell_colour = [0, 0, int(255*(cell_value*-1))]
            # TODO: Figure out why some land cells have negative altitudes
        update_cell_with_colour(indexed_vertex_list, cell_centre_id, cell_colour)

@print_timer
def update_land_cells_with_flat_colour(indexed_vertex_list):
    # Make oceans blue, as otherwise temperature colours may persist
    update_all_cells_to_ocean(indexed_vertex_list)

    nm = everett_importer.world.node_manager
    for cell_centre_id in nm.land_node_ids:
        update_cell_with_colour(indexed_vertex_list, cell_centre_id, land_colour)

@print_timer
def update_ocean_cells_with_ocean_colours(indexed_vertex_list):
    nm = everett_importer.world.node_manager
    for cell_centre_id in nm.ocean_node_ids:
        update_cell_with_colour(indexed_vertex_list, cell_centre_id, ocean_colour)

@print_timer
def update_all_cells_to_ocean(indexed_vertex_list):
    update_all_cells_with_colour(indexed_vertex_list, ocean_colour)

@print_timer
def update_all_cells_with_random_colours(indexed_vertex_list):
    nm = everett_importer.world.node_manager
    for cell_centre_id in nm.cells:
        update_cell_with_colour(indexed_vertex_list, cell_centre_id)

