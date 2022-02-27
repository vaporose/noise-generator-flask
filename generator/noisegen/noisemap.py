import logging
from opensimplex import OpenSimplex
import numpy as np
from PIL import Image
import base64
from io import BytesIO


def generate_2d_noise(height: int,
                      width: int,
                      scale: int = 1,
                      x_offset: int = 0,
                      y_offset: int = 0,
                      seed: str = None) -> np.ndarray:
    """Standalone function, retaining for testing purposes."""

    if seed:
        simplex = OpenSimplex(seed)
        # FIXME this is generating error: seed = overflow(seed * 6364136223846793005 + 1442695040888963407)
    else:
        simplex = OpenSimplex()
    noise_array = np.zeros((height, width))

    for y in range(height):
        for x in range(width):
            ny = (x + x_offset) / scale
            nx = (y + y_offset) / scale
            noise = simplex.noise2(nx, ny)
            noise_array[y][x] = noise

    return noise_array


class NoiseMap:

    def __init__(self, height, width, scale, x_offset, y_offset):

        self._y_offset = y_offset
        self._x_offset = x_offset
        self._scale = scale
        self._width = width
        self._height = height
        self._noise_map = []
        self.simplex = OpenSimplex() # TODO: add seed capacity
        # TODO: Seed in the function or here?

    @property
    def noise_map(self):
        """No setter, use generate_noise_map."""
        return self._noise_map

    def generate_noise_map(self):
        logging.info("Generating the map now")
        # TODO: Feature - add 3D + functions?
        self._noise_map = self.generate_2d_noise()

    def generate_2d_noise(self):
        noise_array = np.zeros((self.height, self.width))

        for y in range(self.height):
            for x in range(self.width):
                ny = (x + self.x_offset) / self.scale
                nx = (y + self.y_offset) / self.scale
                noise = self.simplex.noise2(nx, ny)
                noise_array[y][x] = noise

        return noise_array

    def generate_image(self):
        # TODO currently will error if this is run before setting the map
        image = Image.new("L", (self.height, self.width))
        for y in range(self.height):
            for x in range(self.width):
                color = int((self.noise_map[y][x]+1) * 128)
                image.putpixel((x, y), color)
        image_buffer = BytesIO()
        image.save(image_buffer, "PNG")
        image_data = base64.b64encode(image_buffer.getbuffer()).decode("ascii")
        image_buffer.close()
        return image_data
    
    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height_value):
        self._height = height_value
        self.generate_noise_map()
        
    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, width_value):
        self._width = width_value
        self.generate_noise_map()
        
    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, scale_value):
        self._scale = scale_value
        self.generate_noise_map()
        
    @property
    def x_offset(self):
        return self._x_offset

    @x_offset.setter
    def x_offset(self, x_offset_value):
        self._x_offset = x_offset_value
        self.generate_noise_map()
        
    @property
    def y_offset(self):
        return self._y_offset

    @y_offset.setter
    def y_offset(self, y_offset_value):
        self._y_offset = y_offset_value
        self.generate_noise_map()

