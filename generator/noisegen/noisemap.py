import logging
import uuid
from opensimplex import OpenSimplex
import numpy as np
from PIL import Image
import base64
from io import BytesIO


class NoiseMap:
    """Generates a noise map using simplex (OpenSimplex) noise generation.

    Using the :method:`Noisemap.generate_noise_map`, creates a noise map.
    By default, this only populates the protected _noise_map attribute.

    Currently using :method:`Noisemap.generate_image` to get ascii data of an image to return to web server.

    :param height: The height of the map, in pixels.
    :param width: The width of the map, in pixels.
    :param scale: Feature size to be generated. This divides the X and Y values, essentially "zooming in" to the map.
    :param x_offset: Integer, offsets the returned map on the X axis.
    :param y_offset: Integer, offsets the returned map on the Y axis.
    :param octaves: Each octave adds additional detail to the noise map.
    :param persistence: Float value that is used to decrease the amplitude per octave.
    :param seed: The seed to use for the map generation.

    Usage::

    >>> noise_map = NoiseMap(height=240, width=240, scale=100, octaves=6)
    >>> generated_map = noise_map.generate_noise_map()
    >>> img_data = noise_map.run()
    """

    def __init__(self,
                 height: int = None,
                 width: int = None,
                 scale: int = None,
                 x_offset: int = None,
                 y_offset: int = None,
                 octaves: int = 1,
                 persistence: [int, float] = 0.5,
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
        self._noise_map = []
        self._simplex = OpenSimplex(self.seed)

    def run(self):

        normalized_map = self.generate_noise_map()
        colorized_map = self.terrain_test(normalized_map)
        img_data = self.generate_image(colorized_map)
        return img_data

    def generate_noise_map(self) -> np.ndarray:
        """
        Sets the private _noise_map attribute.

        :return: The noisemap ndarray
        """
        logging.info("Generating the map now")
        # TODO: Feature - add 3D + functions?

        noise_map = self.noise_per_octaves()
        normalized_map = self.normalize_to_1(noise_map)

        return normalized_map

    def noise_per_octaves(self) -> np.ndarray:
        """
        An octave is one layer adding detail to noise.

        Frequency: Doubles per each octave, by default.
        Amplitude: Max possible value of the new pixel. Decreases by the persistence value per each octave.
        :return: Returns the new noise per octaves
        """
        noise_map = np.zeros((self.height, self.width))
        for octave in range(self.octaves):
            amplitude = self.persistence**octave
            frequency = 2**octave
            for (x, y), z in np.ndenumerate(noise_map):
                z += self.generate_2d_noise(x, y, frequency, amplitude)
                noise_map[x][y] = z
        return noise_map

    def normalize_to_1(self, noise_map: np.ndarray) -> np.ndarray:
        """
        Sets all values of the array between 0 and 1.

        Math explanation:
        The minimum value is subtracted both from the minimum value, and the max.
        This makes it so the lowest possible value is 0, since these values were already made positive.
        Dividing a number by the new max value then returns either 1.0 if it's the highest value, or what percentage of
        max it is.

        :param noise_map: ND Array of noise values
        :return: Returns a noise array
        """

        min_value = noise_map.min(initial=0)
        max_value = noise_map.max(initial=1)
        for (x, y), z in np.ndenumerate(noise_map):
            noise_map[x][y] = (z - min_value) / (max_value - min_value)
        return noise_map

    def generate_2d_noise(self, x, y, frequency: int = 1, amplitude: float = .5):
        """
        Frequency = how far apart the points are (sine waves). Higher number = "zoomed out"
        Amplitude = The peak, diminishes over time for adding detail.
        """

        nx = ((x + self.x_offset) / self.scale) * frequency
        ny = ((y + self.y_offset) / self.scale) * frequency
        noise = (self._simplex.noise2(nx, ny) + 1) * amplitude

        return noise

    def terrain_test(self, noise_map: np.ndarray = None):
        if noise_map is None:
            noise_map = self._noise_map

        new_map = np.zeros((self.height, self.width),dtype=tuple)
        water_threshold = (40.0*255)/100
        snow_threshold = (87.0*255)/100
        beach_threshold = (42*255)/100

        for (x, y), z in np.ndenumerate(noise_map):

            lightness = int(z * 255)
            color = None

            if lightness <= water_threshold:
                per_of_max = (lightness/255)*100
                reverse_per = 100 - per_of_max
                reduced_lightness = 255 - ((reverse_per/255)*100)
                color = (0, 0, int(reduced_lightness))  # Blue
            elif lightness <= beach_threshold:
                color = (255, 248, 220)  # Beaches
            elif lightness >= snow_threshold:
                color = (lightness, lightness, lightness)  # Whiteish
            elif water_threshold < lightness < snow_threshold:
                color = (int(lightness/2), lightness, int(lightness/3))  # Green

            new_map[x][y] = color

        return new_map

    def generate_image(self, noise_map: np.ndarray = None):
        if noise_map is None:
            noise_map = self._noise_map
        # TODO currently will error if this is run before setting the map
        image = Image.new("P", (self.width, self.height))
        for (x, y), z in np.ndenumerate(noise_map):
            # if isinstance(float, z):
            #     z = int(z * 255)
            #     color = (z, z, z)
            # else:
            #     color = z
            image.putpixel((x, y), z)

        image_buffer = BytesIO()
        image.save(image_buffer, "PNG")
        image_data = base64.b64encode(image_buffer.getbuffer()).decode("ascii")
        image_buffer.close()
        return image_data

    def to_json(self) -> dict:
        """
        This returns all json-serializable values of this object.

        All non-serializable attributes are set as private
        :return: json-compatible attributes of this class
        """
        json_vars = {key: value for key, value in vars(self).items() if not key.startswith('_')}
        return json_vars
