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
    xRotation = yRotation = 50

    indexed_domain = None
    indexed_vertex_list = None

    def __init__(self, width, height, title=''):
        super(Window, self).__init__(width, height, title)
        glClearColor(0, 0, 0, 1)
        glEnable(GL_DEPTH_TEST)
        self.construct_world_for_drawing()
        everett_importer.update_cells_with_land_colours(self.indexed_vertex_list)

    def construct_world_for_drawing(self):
        num_nodes = 0
        verts = list()
        num_nodes = everett_importer.construct_node_verts(num_nodes, verts)
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

    def draw_water_sphere(self):
        glColor3f(0.015,0.02,0.07)
        sphere = gluNewQuadric()
        gluSphere(sphere, 1.0, 100, 100)

    def on_draw(self):
        # Clear the current GL Window
        self.clear()
        # Push Matrix onto stack
        glPushMatrix()

        glRotatef(self.xRotation, 1, 0, 0)
        glRotatef(self.yRotation, 0, 1, 0)

        self.indexed_vertex_list.draw(pyglet.gl.GL_TRIANGLES)

        # Draw polar line
        pyglet.graphics.draw(2, pyglet.gl.GL_LINES,('v2f', (0, 1.3, 0, -1.3)))

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
            self.yRotation -= rotation_increment
        if keys[key.RIGHT]:
            self.yRotation += rotation_increment

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
