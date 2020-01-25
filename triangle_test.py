from pyglet.gl import *
import math
window = pyglet.window.Window()

planet_centre_coord = [window.width/2, window.height/2]
planet_drawn_radius = window.height/3

# Draw circle
total_p = 120
vertex_list = pyglet.graphics.vertex_list(total_p+1, 'v2f', 'c3B')
vertex_list.vertices[:2] = planet_centre_coord
for p in range(total_p):
    vertex_list.vertices[2*(p+1):2*(p+2)] = [planet_centre_coord[0] + (planet_drawn_radius * math.sin((p/total_p)*2*math.pi)),
                                             planet_centre_coord[1] + (planet_drawn_radius * math.cos((p/total_p)*2*math.pi))]
vertex_list.colors[:] = [0, 0, 255]*(total_p+1)

@window.event
def on_draw():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    #glDrawArrays(GL_TRIANGLES, 0, len(vertices) // 2)
    vertex_list.draw(pyglet.gl.GL_POINTS)

pyglet.app.run()
