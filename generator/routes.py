import base64
from io import BytesIO
from flask.views import MethodView
from flask import render_template, request, jsonify, url_for, make_response, redirect, current_app
from .noisegen.noisemap import NoiseMap
from . import schemas
from PIL import Image

from matplotlib.figure import Figure


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


class TestView(MethodView):
    methods = ["GET", "POST"]

    def get(self):
        # Generate the figure **without using pyplot**.
        fig = Figure()
        ax = fig.subplots()
        ax.plot([1, 2])
        # Save it to a temporary buffer.
        buf = BytesIO()
        fig.savefig(buf, format="png")
        # Embed the result in the html output.
        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        return render_template("index.html", img_data=data)
