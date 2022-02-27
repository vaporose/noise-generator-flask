from flask import Blueprint, request, jsonify
from .noisemap import NoiseMap


noise_bp = Blueprint("noise", __name__, url_prefix="/noise")


@noise_bp.route("/generate/")
def generate_noise():
    # TODO placeholder

    noise_map = NoiseMap(**request.args)
    noise_map.generate_noise_map()
    return jsonify(noise_map)
