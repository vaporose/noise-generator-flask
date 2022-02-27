import logging
import uuid
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

    def __init__(self, height = None, width = None, scale = None, x_offset = None, y_offset = None, noise_map = None, seed = None):

        self.y_offset = y_offset
        self.x_offset = x_offset
        self.scale = scale
        self.width = width
        self.height = height
        self.seed = seed or uuid.uuid1().int >> 64
        self._noise_map = noise_map or []

    def generate_noise_map(self):
        logging.info("Generating the map now")
        # TODO: Feature - add 3D + functions?
        self._noise_map = self.generate_2d_noise()

    def generate_2d_noise(self):
        simplex = OpenSimplex(self.seed)

        noise_array = np.zeros((self.height, self.width))

        for y in range(self.height):
            for x in range(self.width):
                ny = (x + self.x_offset) / self.scale
                nx = (y + self.y_offset) / self.scale
                noise = simplex.noise2(nx, ny)
                noise_array[y][x] = noise

        return noise_array

    def generate_image(self):
        # TODO currently will error if this is run before setting the map
        image = Image.new("L", (self.height, self.width))
        for y in range(self.height):
            for x in range(self.width):
                color = int((self._noise_map[y][x] + 1) * 128)
                image.putpixel((x, y), color)
        image_buffer = BytesIO()
        image.save(image_buffer, "PNG")
        image_data = base64.b64encode(image_buffer.getbuffer()).decode("ascii")
        image_buffer.close()
        return image_data

    def to_json(self):
        json_vars = {key: value for key, value in vars(self).items() if not (key.startswith('_') or callable(value))}
        return json_vars
