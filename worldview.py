import pyglet
from pyglet.gl import *
from pyglet.window import key
from pyglet.window.key import KeyStateHandler

import everett_importer

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
    xRotation = 90
    yRotation = 0
    zRotation = 0

    indexed_domain = None
    indexed_vertex_list = None
    colouring_mode = 0

    def __init__(self, width, height, title=''):
        super(Window, self).__init__(width, height, title)
        glClearColor(0, 0, 0, 1)
        glEnable(GL_DEPTH_TEST)
        self.construct_world_for_drawing()
        self.set_colouring_mode(1)

    def construct_world_for_drawing(self):
        num_nodes = 0
        verts = list()
        num_nodes = everett_importer.construct_node_verts_with_boundary_duplicates(num_nodes, verts)
        print("num nodes: " + str(num_nodes))
        # Create equal number of colour triplets
        vert_colours = everett_importer.construct_blue_colour_list(num_nodes)

        # Create vertex domain defining attribute usage formats
        indexed_domain = pyglet.graphics.vertexdomain.create_indexed_domain('v3f/static', 'c3B/dynamic')

        # Add indices to vertex list
        indices = everett_importer.construct_cell_indices()

        self.indexed_vertex_list = indexed_domain.create(num_nodes, len(indices))
        self.indexed_vertex_list.vertices = verts
        self.indexed_vertex_list.indices = indices
        self.indexed_vertex_list.colors = vert_colours

    def on_draw(self):
        # Clear the current GL Window
        self.clear()
        # Push Matrix onto stack
        glPushMatrix()

        glRotatef(self.xRotation, 1, 0, 0)
        glRotatef(self.yRotation, 0, 1, 0)
        glRotatef(self.zRotation, 0, 0, 1)


        self.indexed_vertex_list.draw(pyglet.gl.GL_TRIANGLES)

        # Draw polar line
        pyglet.graphics.draw(2, pyglet.gl.GL_LINES,('v3f', (0, 0, 1.3, 0, 0, -1.3)))

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
        camera_angle = narrowest_camera_angle + (widest_camera_angle - narrowest_camera_angle)*(1-(current_scroll_level/scroll_levels))
        gluPerspective(camera_angle, aspectRatio, 1, 1000)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        # Camera translation, incorporating mouse scroll
        camera_distance = closest_camera_distance + (furthest_camera_distance - closest_camera_distance)*(1- (current_scroll_level/scroll_levels))
        glTranslatef(0, 0, camera_distance)

    def on_text_motion(self, motion):
        global keys
        if keys[key.UP]:
            self.xRotation -= rotation_increment
        if keys[key.DOWN]:
            self.xRotation += rotation_increment
        if keys[key.LEFT]:
            self.zRotation += rotation_increment
        if keys[key.RIGHT]:
            self.zRotation -= rotation_increment

    def on_key_press(self, symbol, modifiers):
        if symbol == key._1:
            self.set_colouring_mode(1)
        if symbol == key._2:
            self.set_colouring_mode(2)
        if symbol == key._3:
            self.set_colouring_mode(3)
        if symbol == key._4:
            self.set_colouring_mode(4)

    def set_colouring_mode(self, new_render_mode):
        if self.colouring_mode == new_render_mode:
            return
        self.colouring_mode = new_render_mode
        recolour_ocean = False
        # Recolour world
        if self.colouring_mode == 1:
            print("Mode 1. Land colouring")
            everett_importer.update_land_cells_with_flat_colour(self.indexed_vertex_list)
            recolour_ocean = True
        if self.colouring_mode == 2:
            print("Mode 2. Altitude colouring")
            everett_importer.update_land_cells_with_altitude_colours(self.indexed_vertex_list)
            recolour_ocean = True
        if self.colouring_mode == 3:
            print("Mode 3. Whittaker colouring")
            everett_importer.update_land_cells_with_whittaker_colours(self.indexed_vertex_list)
            recolour_ocean = True
        if self.colouring_mode == 4:
            print("Mode 4. Temperature colouring")
            everett_importer.update_cells_with_temperature_colours(self.indexed_vertex_list)

        # Some colouring schemes don't update all cells, so some mop-up is needed
        if recolour_ocean:
            everett_importer.update_ocean_cells_with_ocean_colours(self.indexed_vertex_list)


    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        global current_scroll_level
        global min_scroll
        global max_scroll
        # Update and clamp
        current_scroll_level = min(max(current_scroll_level + scroll_y, 1), scroll_levels)
        self.on_resize(window_width, window_height)


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
