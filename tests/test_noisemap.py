import numpy as np

from generator.noisegen import NoiseMap


def test_heightmap():
    test_map = NoiseMap(240, 240, 1, 0, 0)
    test_map.generate_noise_map()

    assert len(test_map._noise_map) == 240


def test_to_json():
    """Verifies that we can save the output as json and safely recreate it"""
    test_map1 = NoiseMap(240, 240, 1, 0, 0)
    test_map1.generate_noise_map()
    json_output = test_map1.to_json()
    test_map2 = NoiseMap(**json_output)
    test_map2.generate_noise_map()

    assert np.array_equal(test_map1._noise_map, test_map2._noise_map)


