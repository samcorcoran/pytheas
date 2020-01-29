import pyglet
from pyglet.gl import *
from pyglet.window import key
import everett_importer

window_height = 768
window_width = 1080
rotation_increment = 2

class Window(pyglet.window.Window):

    # Cube 3D start rotation
    xRotation = yRotation = 50
    blue_planet_vertex_list = pyglet.graphics.vertex_list(50, 'v2f', 'c3B')
    worldgraph_vertex_list = pyglet.graphics.vertex_list(1, 'v3f', 'c3B')

    def __init__(self, width, height, title=''):
        super(Window, self).__init__(width, height, title)
        glClearColor(0, 0, 0, 1)
        glEnable(GL_DEPTH_TEST)
        everett_importer.construct_blue_circle(self.blue_planet_vertex_list)
        everett_importer.construct_worldgraph_verts(self.worldgraph_vertex_list)

    def on_draw(self):
        # Clear the current GL Window
        self.clear()
        # Push Matrix onto stack
        glPushMatrix()

        glRotatef(self.xRotation, 1, 0, 0)
        glRotatef(self.yRotation, 0, 1, 0)

        #self.blue_planet_vertex_list.draw(pyglet.gl.GL_TRIANGLE_FAN)
        self.worldgraph_vertex_list.draw(pyglet.gl.GL_POINTS)

        glPopMatrix()

        #window.flip()

    def on_resize(self, width, height):
        # set the Viewport
        glViewport(0, 0, width, height)

        # using Projection mode
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        aspectRatio = width / height
        gluPerspective(90, aspectRatio, 1, 1000)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        # Camera translation
        glTranslatef(0, 0, -25)


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