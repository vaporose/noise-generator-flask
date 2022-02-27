from flask import render_template, request, jsonify, url_for, redirect, current_app
from flask.views import MethodView

from . import schemas
from .noisegen import NoiseMap


class IndexView(MethodView):
    methods = ["GET", "POST"]

    def get(self):

        return render_template("index.html")

    def post(self):
        schema = schemas.FormSchema()  # Easy way to convert form data strings to their needed types.
        form = schema.load(request.form)

        noise_array = NoiseMap(**form)
        noise_array.generate_noise_map()
        data = noise_array.generate_image()

        return render_template("index.html", img_data=data)


