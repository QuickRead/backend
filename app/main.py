from flask import Flask


def create_app():
    app = Flask(__name__)

    @app.route('/')
    def health_check():
        return "OK"

    return app
