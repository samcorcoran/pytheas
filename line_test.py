import pyglet
from pyglet.gl import *

w = pyglet.window.Window(width=1024, height=720)
glMatrixMode(GL_PROJECTION)
glLoadIdentity()
glViewport(0, 0, 1024, 720)
glOrtho(0, 1024, 0, 720, -1000, 1000)
glMatrixMode(GL_MODELVIEW)
glClearColor(1, 1, 1, 1)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
glPolygonMode(GL_BACK, GL_LINE)

coords = []
batch = pyglet.graphics.Batch()
vertex_list = None

@w.event
def on_draw():
    glColor3f(1, 1, 1)
    glPolygonMode(GL_FRONT, GL_LINE)
    glBegin(GL_LINE_STRIP)
    for x, y, z in coords:
        glVertex3f(x, y, z)
    glEnd()


    pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
                         ('v3f', (10, 15, 0, 30, 35, 0)),
                         ('c3B', (0, 0, 255, 0, 255, 0))
                         )

def build_batches():
    vertex_list = batch.add(len(coords)//3, pyglet.gl.GL_LINES, None,
                            ('v3f', coords),
                            ('c3B', (0, 0, 255, 0, 255, 0))
                            )

def update_batches():
    vertex_list.verts

@w.event
def on_mouse_press(x, y, button, modifiers):
    coords.append((x, y, 0))
    build_batches()
    print(coords)


build_batches()
pyglet.app.run()
