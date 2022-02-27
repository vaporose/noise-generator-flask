import logging

from flask import render_template, request, jsonify, url_for, redirect, current_app, session
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

        session_values = session.get("noise_map", None)
        if session_values:
            session_values.update(form)
            noise_map = NoiseMap(**session_values)
        else:
            noise_map = NoiseMap(**form)

        noise_map.generate_noise_map()
        session["noise_map"] = noise_map.to_json()
        data = noise_map.generate_image()

        return render_template("index.html", img_data=data)


