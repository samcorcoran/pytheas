from pyglet.gl import *
import math
from everett.worldgraph import world
from everett.worldgenerators import world_three

world = world_three.generate_world(total_cells_desired=5000)

window = pyglet.window.Window()

planet_centre_coord = [window.width/2, window.height/2]
planet_drawn_radius = window.height/3

# Construct circle
circle_sides = 50
blue_planet_vertex_list = pyglet.graphics.vertex_list(circle_sides+2, 'v2f', 'c3B')
blue_planet_vertex_list.vertices[:2] = planet_centre_coord
for p in range(circle_sides):
    blue_planet_vertex_list.vertices[2*(p+1):2*(p+2)] = [planet_centre_coord[0] + (planet_drawn_radius * math.sin((p/circle_sides)*2*math.pi)),
                                                         planet_centre_coord[1] + (planet_drawn_radius * math.cos((p/circle_sides)*2*math.pi))]
blue_planet_vertex_list.vertices[-2:] = [planet_centre_coord[0] + (planet_drawn_radius * math.sin(2*math.pi)),
                                         planet_centre_coord[1] + (planet_drawn_radius * math.cos(2*math.pi))]

blue_planet_vertex_list.colors[:] = [0, 0, 255]* (len(blue_planet_vertex_list.vertices)//2)

# Construct worldgraph verts
verts = list()
worldgraph_vertex_list = pyglet.graphics.vertex_list(len(world.node_manager.cartesian_locs.values()), 'v3f', 'c3B')
for p in world.node_manager.cartesian_locs.values():
    verts.extend([planet_centre_coord[0]+(p[0]*planet_drawn_radius),
                 planet_centre_coord[1]+(p[1]*planet_drawn_radius),
                 0])
worldgraph_vertex_list.vertices[:] = verts
worldgraph_vertex_list.colors[:] = [255, 0, 0]*len(world.node_manager.cartesian_locs.values())


@window.event
def on_draw():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    #glDrawArrays(GL_TRIANGLES, 0, len(vertices) // 2)
    blue_planet_vertex_list.draw(pyglet.gl.GL_TRIANGLE_FAN)
    worldgraph_vertex_list.draw(pyglet.gl.GL_POINTS)

pyglet.app.run()
