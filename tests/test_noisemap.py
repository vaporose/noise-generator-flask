import numpy

from generator.noisegen import NoiseMap


def test_heightmap():
    test_map = NoiseMap(240, 240, 1, 0, 0)
    test_map.generate_noise_map()

    assert len(test_map.noise_map) == 240
