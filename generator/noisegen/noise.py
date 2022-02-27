from opensimplex import OpenSimplex
import numpy as np
from PIL import Image
import base64
from io import BytesIO


def grayscale_image_data_from_noisemap(noise_array: np.ndarray, height: int, width: int):
    image = Image.new("L", (height, width))
    for y in range(height):
        for x in range(width):
            color = int(noise_array[y][x] * 128)
            image.putpixel((x, y), color)
    image_buffer = BytesIO()
    image.save(image_buffer, "PNG")

    data = base64.b64encode(image_buffer.getbuffer()).decode("ascii")
    image_buffer.close()
    return data

def generate_2d_noise(height: int,
                      width: int,
                      scale: int = 1,
                      x_offset: int = 0,
                      y_offset: int = 0,
                      seed: str = None) -> np.ndarray:
    if seed:
        simplex = OpenSimplex(seed)
        # TODO generating error: seed = overflow(seed * 6364136223846793005 + 1442695040888963407)
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
