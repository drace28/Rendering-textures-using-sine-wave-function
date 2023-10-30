import pygame as pg
import moderngl as mgl
import struct
import sys


class Quad(pg.sprite.Sprite):
    def __init__(self, win_size):
        super().__init__()
        self.image = pg.Surface(win_size, pg.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = win_size[0] // 2, win_size[1] // 2

        # Quad vertices
        self.vertices = [(-1, -1), (1, -1), (1, 1), (-1, 1), (-1, -1), (1, 1)]

        # Set up Pygame drawing context
        self.ctx = pg.display.get_surface()

        # Load shaders (Make sure file paths are correct)
        with open("vertex.glsl") as f:
            vertex = f.read()
        with open("fragment.glsl") as f:
            fragment = f.read()
        self.program = pg.gl.GLProgram(vertex, fragment)

        # Uniforms
        self.set_uniform('u_resolution', win_size)

    def set_uniform(self, u_name, u_value):
        try:
            self.program.uniforms[u_name] = u_value
        except KeyError:
            raise ValueError(f"Uniform '{u_name}' not found in shader program")

    def update(self, dt):
        self.set_uniform('u_time', pg.time.get_ticks() * 0.001)

    def draw(self):
        # Clear the screen
        self.ctx.fill((0, 0, 0))

        # Draw the quad
        pg.draw.polygon(self.image, (255, 255, 255), self.vertices)

        # Render the quad using the shader program
        self.program.use()
        pg.gl.glDrawArrays(pg.gl.GL_TRIANGLES, 0, len(self.vertices))
class App:
    def __init__(self, win_size=(1600, 900)):
        # Initialize Pygame
        pg.init()
        
        # Create a Pygame display
        pg.display.set_mode(win_size, pg.OPENGL | pg.DOUBLEBUF)
        
        # OpenGL context
        self.ctx = mgl.create_context()

        # Time objects
        self.clock = pg.time.Clock()

        # Load shaders (Make sure file paths are correct)
        with open("vertex.glsl") as f:
            vertex = f.read()
        with open("fragment.glsl") as f:
            fragment = f.read()
        self.program = self.ctx.program(vertex_shader=vertex, fragment_shader=fragment)

        # Quad screen vertices
        vertices = [(-1,-1), (1, -1), (1, 1), (-1, 1), (-1, -1), (1, 1)]

        # Quad VBO
        vertex_data = struct.pack(f'{len(vertices) * len(vertices[0])}f', *sum(vertices, ()))
        self.vbo = self.ctx.buffer(vertex_data)

        # Quad VAO
        self.vao = self.ctx.simple_vertex_array(self.program, self.vbo, 'in_position')

        # Uniforms
        self.set_uniform('u_resolution', win_size)

    def render(self):
        self.ctx.clear()
        self.vao.render()
        pg.display.flip()

    def update(self):
        self.set_uniform('u_time', pg.time.get_ticks() * 0.001)

    def run(self):
        while True:
            self.check_events()
            self.update()
            self.render()
            self.clock.tick(60)  # Limit the frame rate to 60 FPS
            fps = self.clock.get_fps()
            pg.display.set_caption(f'{fps :.1f}')

    def set_uniform(self, u_name, u_value):
        try:
            self.program[u_name].value = u_value
        except KeyError:
            raise ValueError(f"Uniform '{u_name}' not found in shader program")

    def destroy(self):
        self.vbo.release()
        self.program.release()
        self.vao.release()

    def check_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                self.destroy()
                pg.quit()
                sys.exit()

if __name__ == '__main__':
    app = App()
    app.run()
