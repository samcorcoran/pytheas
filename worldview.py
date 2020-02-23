import pyglet
from pyglet.gl import *
from pyglet.window import key
import everett_importer

window_height = 780
window_width = 1080
rotation_increment = 2

class Window(pyglet.window.Window):

    # Cube 3D start rotation
    xRotation = yRotation = 50

    indexed_domain = None
    indexed_vertex_list = None

    cell_bp_nums = dict()

    def __init__(self, width, height, title=''):
        super(Window, self).__init__(width, height, title)
        glClearColor(0, 0, 0, 1)
        glEnable(GL_DEPTH_TEST)
        self.construct_world_for_drawing()

    def construct_world_for_drawing(self):
        num_nodes = 0
        verts = list()
        node_ids_to_vert_idx = dict()
        num_nodes = everett_importer.construct_node_verts(num_nodes, verts, node_ids_to_vert_idx)
        print("num nodes: " + str(num_nodes))
        # Create equal number of colour triplets
        vert_colours = everett_importer.construct_blue_colour_list(num_nodes)

        # Create vertex domain defining attribute usage formats
        indexed_domain = pyglet.graphics.vertexdomain.create_indexed_domain('v3f/static', 'c3B/dynamic')

        # Add indices to vertex list
        indices = everett_importer.construct_cell_indices(node_ids_to_vert_idx)

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

        # TODO: Don't define new sphere on every draw?
        #self.draw_water_sphere()

        #self.cell_vertex_list.draw(pyglet.gl.GL_TRIANGLES)
        self.indexed_vertex_list.draw(pyglet.gl.GL_TRIANGLES)
        glPopMatrix()

        #window.flip()

    def on_resize(self, width, height):
        # set the Viewport
        glViewport(0, 0, width, height)

        # using Projection mode
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        aspectRatio = width / height
        camera_angle = 60
        gluPerspective(camera_angle, aspectRatio, 1, 1000)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        # Camera translation
        camera_distance = -3
        glTranslatef(0, 0, camera_distance)

    def on_text_motion(self, motion):
        if motion == key.UP:
             self.xRotation -= rotation_increment
        elif motion == key.DOWN:
            self.xRotation += rotation_increment
        elif motion == key.LEFT:
            self.yRotation -= rotation_increment
        elif motion == key.RIGHT:
            self.yRotation += rotation_increment


if __name__ == '__main__':
   Window(window_width, window_height, 'Everett Worldview')
   pyglet.app.run()