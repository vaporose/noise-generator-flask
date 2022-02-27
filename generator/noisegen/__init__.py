from flask import Blueprint, request, jsonify
from .noise import generate_2d_noise


noise_bp = Blueprint("noise", __name__, url_prefix="/noise")


@noise_bp.route("/generate/")
def generate_noise():
    height: int = request.args.get("height", 240)
    width: int = request.args.get("height", 240)
    scale: int = request.args.get("scale", 1)
    x_offset: int = request.args.get("x_offset", 0)
    y_offset: int = request.args.get("y_offset", 0)
    seed: int = request.args.get("seed", 0)

    noise_map = generate_2d_noise(height, width, scale, x_offset, y_offset, seed)
    return jsonify(noise_map)
