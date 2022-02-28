import logging
import uuid
from opensimplex import OpenSimplex
import numpy as np
from PIL import Image
import base64
from io import BytesIO


class NoiseMap:

    def __init__(self,
                 height: int = None,
                 width: int = None,
                 scale: int = None,
                 x_offset: int = None,
                 y_offset: int = None,
                 octaves: int = 1,
                 persistence: [int, float] = 0.5,
                 noise_map=None,
                 seed=None):

        persistence = float(persistence)
        if persistence > 1.0:
            persistence *= 100
        self.persistence = persistence
        self.octaves = octaves
        self.y_offset = y_offset
        self.x_offset = x_offset
        self.scale = scale
        self.width = width
        self.height = height
        self.seed = seed or uuid.uuid1().int >> 64
        self._noise_map = noise_map or []  # Future compatibility
        self._simplex = OpenSimplex(self.seed)

    def generate_noise_map(self):
        logging.info("Generating the map now")
        # TODO: Feature - add 3D + functions?
        noise_map = np.zeros((self.height, self.width))
        for octave in range(self.octaves):
            amplitude = self.persistence**octave
            frequency = 2**octave
            for (x, y), z in np.ndenumerate(noise_map):
                z += self.generate_2d_noise(x, y, frequency, amplitude)
                noise_map[x][y] = z

        # Normalizes values between 0 and 1
        min_value = noise_map.min(initial=0)
        max_value = noise_map.max(initial=1)
        for (x, y), z in np.ndenumerate(noise_map):
            new_z = (z - min_value) / (max_value - min_value)
            noise_map[x][y] = new_z

        self._noise_map = noise_map

    def generate_2d_noise(self, x, y, frequency: int = 1, amplitude: float = .5):
        """
        Frequency = how far apart the points are (sine waves). Higher number = "zoomed out"
        Amplitude = The peak, diminishes over time for adding detail.
        """

        nx = ((x + self.x_offset) / self.scale) * frequency
        ny = ((y + self.y_offset) / self.scale) * frequency
        noise = (self._simplex.noise2(nx, ny) + 1) * amplitude

        return noise

    def generate_image(self):
        # TODO currently will error if this is run before setting the map
        image = Image.new("L", (self.width, self.height))
        for (x, y), z in np.ndenumerate(self._noise_map):
            image.putpixel((x, y), int(z * 255))

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
