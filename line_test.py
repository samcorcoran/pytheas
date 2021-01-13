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

coords = [30, 15, 0, 50, 35, 0]
batch = pyglet.graphics.Batch()
v_list = None

@w.event
def on_draw():

    glColor3f(1, 1, 1)
    glPolygonMode(GL_FRONT, GL_LINE)
    glBegin(GL_LINES)
    #for x, y, z in coords:
        #glVertex3f(x, y, z)
    glEnd()

    batch.draw()

    # This renders correctly
    pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
                         ('v3f', (10, 15, 0, 30, 35, 0)),
                         ('c3B', (0, 0, 255, 0, 255, 0))
                         )

def build_batches():
    global v_list
    global batch
    num_verts = len(coords)//3
    print(num_verts)
    v_list = batch.add(num_verts, pyglet.gl.GL_LINES, None,
                            ('v3f', coords),
                            ('c3B', [0, 0, 255]*num_verts)
                            )

    # This renders correctly
    v_list_2 = batch.add(2, pyglet.gl.GL_LINES, None, ('v3f', [20, 15, 0, 40, 35, 0]), ('c3B', [255, 0, 0, 255, 0, 0]))

def update_batches():
    global v_list
    num_verts = len(coords)//3
    print(num_verts)
    print("That was len")
    v_list.delete()
    v_list = batch.add(num_verts, pyglet.gl.GL_LINES, None, ('v3f', coords), ('c3B', [0, 0, 255]*num_verts))
    v_list.vertices = coords

@w.event
def on_mouse_press(x, y, button, modifiers):
    coords.extend([x, y, 0])
    print("{} coords".format(len(coords)//3))
    for i in range(0, len(coords), 3):
        x1 = coords[i:i+3]
        print(x1)
    update_batches()

build_batches()
pyglet.app.run()
