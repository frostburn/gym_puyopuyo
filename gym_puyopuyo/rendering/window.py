from gym_puyopuyo.rendering.state import Garbage, Pop


class SpriteSheet(object):
    BLOCK_WIDTH = 31

    def __init__(self, filename="plain_skin.png"):
        import pyglet  # Needs to be a local import to make the package load without a display.
        self.sheet = pyglet.image.load(filename)
        self.grid = pyglet.image.ImageGrid(self.sheet, 16, 16)

    def get_sprite(self, entity, neighbours):
        if isinstance(entity, Garbage):
            return self.grid[3, 6]
        elif isinstance(entity, Pop):
            return self.grid[5, 6 + 2 * entity.color + entity.age]
        neighbours = [n == entity for n in neighbours]
        index = neighbours[0] + 2 * neighbours[1] + 4 * neighbours[2] + 8 * neighbours[3]
        color = entity.color
        # Shuffle colors to be consistent with ansi rendering
        if color == 2:
            color = 3
        elif color == 3:
            color = 2
        return self.grid[15 - color, index]


class ImageViewer(object):
    def __init__(self, display=None):
        from pyglet.window import Window
        self.display = display
        self.window = Window(width=512, height=512, display=self.display)
        self.isopen = True
        self.sheet = SpriteSheet()
        self.init_blend()

    def init_blend(self):
        from pyglet.gl import (
            GL_BLEND, GL_ONE_MINUS_SRC_ALPHA, GL_SRC_ALPHA, glBlendFunc, glEnable
        )
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def render_state(self, state):
        self.window.clear()
        self.window.switch_to()
        self.window.dispatch_events()
        for i, entity in enumerate(state.entities):
            if entity is None:
                continue
            y, x = divmod(i, state.width)
            neighbours = [None] * 4
            neighbours[1] = state[x, y - 1]
            neighbours[0] = state[x, y + 1]
            neighbours[3] = state[x - 1, y]
            neighbours[2] = state[x + 1, y]
            sprite = self.sheet.get_sprite(entity, neighbours)
            sprite.blit(
                x * self.sheet.BLOCK_WIDTH,
                (state.height - 1 - y) * self.sheet.BLOCK_WIDTH,
            )
        for i, deal in enumerate(state.deals):
            for j, entity in enumerate(deal):
                neighbours = [None] * 4
                # Deals are usually not rendered "sticky"
                # neighbours[2 + j] = deal[1 - j]
                sprite = self.sheet.get_sprite(entity, neighbours)
                sprite.blit(
                    (state.width + 2 + j) * self.sheet.BLOCK_WIDTH,
                    (state.height - 1 - 2 * i) * self.sheet.BLOCK_WIDTH,
                )
        self.window.flip()

    def save_screenshot(self, filename):
        from pyglet.image import get_buffer_manager
        get_buffer_manager().get_color_buffer().save(filename)

    def close(self):
        if self.isopen:
            self.window.close()
            self.isopen = False

    def __del__(self):
        self.close()
