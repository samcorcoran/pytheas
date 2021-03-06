import pyglet
from pyglet.gl import *
from pyglet.window import key
from pyglet.window.key import KeyStateHandler
from everett_importer import construct_blue_colour_list

import pytheas_config as config
import everett_importer
import cell_colouring

window_height = 780
window_width = 1080
rotation_increment = 2

# Scrolling
scroll_levels = 20
current_scroll_level = 5
# Camera distance scrolling
closest_camera_distance = -2
furthest_camera_distance = -3
# Camera angle scrolling
widest_camera_angle = 100
narrowest_camera_angle = 10

keys = None

class Window(pyglet.window.Window):
    # Cube 3D start rotation
    xRotation = defaultXRotation = 90
    yRotation = defaultYRotation = 0
    zRotation = defaultZRotation = 0

    # 90, 0, 0 degrees == 0N 0E lon lat
    # <90 xRot is south pole
    # >90 xRot is north pole
    # 90 zRot is Asia
    # So...
    # Latitude = xRotation - 90
    # Longitude = zRotation

    indexed_domain = None
    indexed_vertex_list = None
    flat_indexed_vertex_list = None
    paths_indexed_vertex_list = None
    batch_paths = None

    colouring_mode = 0
    numbered_options = None
    mode_is_3d = True
    dirty_verts = False

    def __init__(self, width, height, title=''):
        super(Window, self).__init__(width, height, title)
        glClearColor(0, 0, 0, 1)
        glEnable(GL_DEPTH_TEST)
        pyglet.gl.glLineWidth(config.path_line_width)
        self.set_up_options_ui()

        self.construct_world_for_drawing()
        self.set_colouring_mode(1)

    def set_up_options_ui(self):
        self.set_numbered_options()

    def construct_world_for_drawing(self):
        self.construct_3d_world()
        self.construct_2d_world()

    def construct_3d_world(self):
        self.batch_paths = pyglet.graphics.Batch()

        """For 3D rendering of everett world, create pyglet indexed domain of vertices and colours."""
        verts, num_verts = everett_importer.construct_node_verts_with_boundary_duplicates()

        # Create equal number of colour triplets
        vert_colours = construct_blue_colour_list(num_verts)

        # Create vertex domain defining attribute usage formats
        indexed_domain = pyglet.graphics.vertexdomain.create_indexed_domain('v3f/static', 'c3B/dynamic')

        # Add indices to vertex list
        indices = everett_importer.construct_cell_indices()

        self.indexed_vertex_list = indexed_domain.create(num_verts, len(indices))
        self.indexed_vertex_list.vertices = verts
        self.indexed_vertex_list.indices = indices
        self.indexed_vertex_list.colors = vert_colours

        # Paths, for rivers etc
        everett_importer.construct_3d_paths(self.batch_paths)

    def construct_2d_world(self):
        # Generate verts
        verts_2d, num_nodes_2d = everett_importer.construct_2d_node_verts_with_boundary_duplicates(self.zRotation-self.defaultZRotation)

        if self.flat_indexed_vertex_list is not None:
            return
        # Create vertex domain defining attribute usage formats
        flat_indexed_domain = pyglet.graphics.vertexdomain.create_indexed_domain('v3f/dynamic', 'c3B/dynamic')
        # Add indices to vertex list
        indices = everett_importer.construct_cell_indices()
        self.flat_indexed_vertex_list = flat_indexed_domain.create(num_nodes_2d, len(indices))
        self.flat_indexed_vertex_list.vertices = verts_2d
        self.flat_indexed_vertex_list.indices = self.indexed_vertex_list.indices
        self.flat_indexed_vertex_list.colors = self.indexed_vertex_list.colors

    def reconstruct_2d_world(self):
        # Rebuild vertex information based on new 2d positions for cells (e.g. if wrapping at back of globe has changed)
        verts_2d, num_verts_2d = everett_importer.construct_2d_node_verts_with_boundary_duplicates(self.zRotation-self.defaultZRotation)
        # Populate vertex list with vertex information
        self.flat_indexed_vertex_list.vertices = verts_2d
        self.flat_indexed_vertex_list.indices = self.indexed_vertex_list.indices

    def on_draw(self):
        # TODO: Find out why this is being called twice on every key press (dirty_verts is being used as a mitigation)
        # Clear the current GL Window
        self.clear()
        # Push Matrix onto stack
        glPushMatrix()
        if self.mode_is_3d:
            # TODO: Remove this magic number by positioning the camera differently? Also, fix that perspective warping...
            z_rotation_to_make_3d_and_2d_match = 90
            glRotatef(self.xRotation, 1, 0, 0)
            glRotatef(self.yRotation, 0, 1, 0)
            glRotatef(self.zRotation+z_rotation_to_make_3d_and_2d_match, 0, 0, 1)
        else:
            glRotatef(self.defaultXRotation, 1, 0, 0)
            glRotatef(self.defaultYRotation, 0, 1, 0)
            glRotatef(self.defaultZRotation, 0, 0, 1)

        if self.dirty_verts:
            if not self.mode_is_3d:
                self.reconstruct_2d_world()
                self.dirty_verts = False

        # Draw coloured triangles to form cells
        if self.mode_is_3d:
            self.indexed_vertex_list.draw(pyglet.gl.GL_TRIANGLES)
            #self.paths_indexed_vertex_list.draw(pyglet.gl.GL_LINE_STRIP)
            self.batch_paths.draw()
        else:
            self.flat_indexed_vertex_list.draw(pyglet.gl.GL_TRIANGLES)
        # Draw polar line
        pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ('v3f', (0, 0, 1.3, 0, 0, -1.3)))
        glPopMatrix()

    def on_resize(self, width, height):
        # set the Viewport
        glViewport(0, 0, width, height)

        # using Projection mode
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        aspectRatio = width / height
        global max_scroll, max_camera_angle, default_camera_angle
        scroll = max(current_scroll_level, 0) / (scroll_levels)
        camera_angle = narrowest_camera_angle + (widest_camera_angle - narrowest_camera_angle) * (
            1 - (current_scroll_level / scroll_levels))
        gluPerspective(camera_angle, aspectRatio, 1, 1000)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        # Camera translation, incorporating mouse scroll
        camera_distance = closest_camera_distance + (furthest_camera_distance - closest_camera_distance) * (
            1 - (current_scroll_level / scroll_levels))
        glTranslatef(0, 0, camera_distance)

    def on_text_motion(self, motion):
        global keys
        if self.mode_is_3d:
            if keys[key.UP]:
                self.xRotation -= rotation_increment
            if keys[key.DOWN]:
                self.xRotation += rotation_increment
        # Left and right are permitted in 2D
        if keys[key.LEFT]:
            self.zRotation += rotation_increment
        if keys[key.RIGHT]:
            self.zRotation -= rotation_increment
        self.clamp_rotations()
        self.dirty_verts = True

    def clamp_rotations(self):
        """
        Called after rotation updates, to keep rotation values within controlled range.
        """
        # Clamp longitudinal (Z) rotation to valid longitudes
        if self.zRotation <= -180:
            self.zRotation = self.zRotation + 360
        if self.zRotation > 180:
            self.zRotation = self.zRotation - 360
        self.xRotation = self.xRotation % 360
        self.yRotation = self.yRotation % 360

    def on_key_press(self, symbol, modifiers):
        if symbol == key._1:
            self.set_colouring_mode(1)
        if symbol == key._2:
            self.set_colouring_mode(2)
        if symbol == key._3:
            self.set_colouring_mode(3)
        if symbol == key._4:
            self.set_colouring_mode(4)
        if symbol == key._5:
            self.set_colouring_mode(5)
        if symbol == key._6:
            self.set_colouring_mode(6)
        if symbol == key._7:
            self.set_colouring_mode(7)
        if symbol == key._8:
            self.set_colouring_mode(8)
        if symbol == key._9:
            self.set_colouring_mode(9)
        if symbol == key._0:
            self.set_colouring_mode(0)

    def set_colouring_mode(self, new_render_mode):
        self.colouring_mode = new_render_mode
        # Recolour world
        print("%s%d%s %s" % ("Mode ", new_render_mode, ".", self.numbered_options[new_render_mode][0]))
        self.numbered_options[new_render_mode][1](self.indexed_vertex_list)
        # Update 2D vertices with same colours
        self.flat_indexed_vertex_list.colors = self.indexed_vertex_list.colors


    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        global current_scroll_level
        global min_scroll
        global max_scroll
        # Update and clamp
        current_scroll_level = min(max(current_scroll_level + scroll_y, 1), scroll_levels)
        self.on_resize(window_width, window_height)

    def set_numbered_options(self):
        self.numbered_options = list(range(10))
        self.numbered_options[1] = ['Land colouring', cell_colouring.update_land_cells_with_flat_colour]
        self.numbered_options[2] = ['Altitude colouring', cell_colouring.update_land_cells_with_altitude_colours]
        self.numbered_options[3] = ['Whittaker colouring', cell_colouring.update_land_cells_with_whittaker_colours]
        self.numbered_options[4] = ['Temperature colouring', cell_colouring.update_cells_with_temperature_colours]
        self.numbered_options[5] = ['Toggle 2D/3D', self.toggle_2d_3d_mode]
        self.numbered_options[6] = ['', print("Option 6 not set.")]
        self.numbered_options[7] = ['', print("Option 7 not set.")]
        self.numbered_options[8] = ['', print("Option 8 not set.")]
        self.numbered_options[9] = ['', print("Option 9 not set.")]
        self.numbered_options[0] = ['Reset ocean blues', cell_colouring.update_ocean_cells_with_ocean_colours]

    def toggle_2d_3d_mode(self, indexed_vertex_list):
        self.mode_is_3d = not self.mode_is_3d

def main():
    global keys
    everett_importer.generate_world()

    window = Window(window_width, window_height, 'Everett Worldview')
    keys = KeyStateHandler()
    window.push_handlers(keys)

    pyglet.app.run()


def exit_app():
    pyglet.app.exit()


if __name__ == '__main__':
    main()
