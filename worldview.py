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
    worldgraph_vertex_list = pyglet.graphics.vertex_list(1, 'v3f', 'c3B')
    cell_vertex_list = pyglet.graphics.vertex_list(1, 'v3f', 'c3B')
    cell_bp_nums = dict()

    def __init__(self, width, height, title=''):
        super(Window, self).__init__(width, height, title)
        glClearColor(0, 0, 0, 1)
        glEnable(GL_DEPTH_TEST)
        everett_importer.construct_cell_vertex_list(self.cell_vertex_list, self.cell_bp_nums)
        everett_importer.update_cells_with_land_colours(self.cell_vertex_list, self.cell_bp_nums)

    def draw_water_sphere(self):
        glColor3f(0.015,0.02,0.07)
        sphere = gluNewQuadric()
        gluSphere(sphere, 10.0, 100, 100)

    def on_draw(self):
        # Clear the current GL Window
        self.clear()
        # Push Matrix onto stack
        glPushMatrix()

        glRotatef(self.xRotation, 1, 0, 0)
        glRotatef(self.yRotation, 0, 1, 0)

        # TODO: Don't define new sphere on every draw?
        #self.draw_water_sphere()

        self.cell_vertex_list.draw(pyglet.gl.GL_TRIANGLES)

        glPopMatrix()

        #window.flip()

    def on_resize(self, width, height):
        # set the Viewport
        glViewport(0, 0, width, height)

        # using Projection mode
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        aspectRatio = width / height
        gluPerspective(60, aspectRatio, 1, 1000)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        # Camera translation
        glTranslatef(0, 0, -2.25)


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