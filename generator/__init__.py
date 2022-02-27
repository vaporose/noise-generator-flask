from flask import Flask
from . import routes


from flask_bootstrap import Bootstrap5


def create_app():

    app = Flask("generator")
    app.config["BOOTSTRAP_BOOTSWATCH_THEME"] = "united"
    app.config["SECRET_KEY"] = "FRODO BAGGINS"  # TODO use secure thing
    bootstrap = Bootstrap5(app)

    from .noisegen import noise_bp
    app.register_blueprint(noise_bp)

    app.add_url_rule("/", view_func=routes.IndexView.as_view("index"))

    return app
