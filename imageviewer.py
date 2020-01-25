import pyglet
import pyglet.gl

width = 1000
height = 1000

window = pyglet.window.Window(960, 640)
image = pyglet.resource.image('resources/pomeranian.jpg')

def centre_image(image):
    """Sets an image's anchor point to its center"""
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2

@window.event
def on_draw():
    window.clear()
    image.blit(0, 0)
    centre_image(image)

pyglet.app.run()
