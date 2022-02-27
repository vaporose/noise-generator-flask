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

    def __init__(self,
                 height: int = None,
                 width: int = None,
                 scale: int = None,
                 x_offset: int = None,
                 y_offset: int = None,
                 octaves: int = 1,
                 noise_map=None,
                 seed=None):

        self.octaves = octaves
        self.y_offset = y_offset
        self.x_offset = x_offset
        self.scale = scale
        self.width = width
        self.height = height
        self.seed = seed or uuid.uuid1().int >> 64
        self._noise_map = noise_map or []  # Future compatibility

    def generate_noise_map(self):
        logging.info("Generating the map now")
        # TODO: Feature - add 3D + functions?
        noise_map = None
        persistence = 0.5
        for octave in range(self.octaves):
            amplitude = persistence**octave
            frequency = 2**octave
            print(f"{amplitude}, {frequency}")
            current_map = self.generate_2d_noise(frequency)
            # TODO this definitely can be done better
            if noise_map is not None:
                for y in range(self.height):
                    for x in range(self.width):
                        noise_map[y][x] += (current_map[y][x] * amplitude)

            else:
                noise_map = current_map

        self._noise_map = noise_map


    def generate_2d_noise(self, frequency: int = 1):
        simplex = OpenSimplex(self.seed)

        # TODO I think there's a better way to use numpy here
        noise_array = np.zeros((self.height, self.width))

        for y in range(self.height):
            for x in range(self.width):
                ny = (x + self.x_offset) / self.scale
                nx = (y + self.y_offset) / self.scale
                noise = simplex.noise2(nx * frequency, ny * frequency) + 1
                noise_array[y][x] = noise

        min_value = noise_array.min(initial=0)
        max_value = noise_array.max(initial=1)  # TODO replace with numpy
        for y in range(self.height):
            for x in range(self.width):
                z = (noise_array[y][x] - min_value) / (max_value - min_value)
                noise_array[y][x] = z

        return noise_array

    def generate_image(self):
        # TODO currently will error if this is run before setting the map
        image = Image.new("L", (self.width, self.height))
        for y in range(self.height):
            for x in range(self.width):
                # TODO need to learn better what to do with this
                color = int(self._noise_map[y][x] * 128)
                try:
                    image.putpixel((x, y), color)
                except IndexError as err:
                    logging.error(f"Trying to put in {x},{y}. Width/Height: {self.width}/{self.height}")
                    logging.error(err)
        image_buffer = BytesIO()
        image.save(image_buffer, "PNG")
        image_data = base64.b64encode(image_buffer.getbuffer()).decode("ascii")
        image_buffer.close()
        return image_data

    def to_json(self) -> dict:
        """
        This returns all json-serializable values of this object.

        All non-serializable attributes are set as private
        :return:
        """
        json_vars = {key: value for key, value in vars(self).items() if not key.startswith('_')}
        return json_vars
