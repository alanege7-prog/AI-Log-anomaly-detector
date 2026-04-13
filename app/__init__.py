import os
import threading
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

_basedir = os.path.abspath(os.path.dirname(__file__))


def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(_basedir, '..', 'templates'),
        static_folder=os.path.join(_basedir, '..', 'static'),
    )
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        'sqlite:///' + os.path.join(_basedir, '..', 'alerts.db')
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from .routes import bp
    app.register_blueprint(bp)

    with app.app_context():
        db.create_all()

    return app


def start_background_watcher(app):
    from .watcher import watch_log
    t = threading.Thread(target=watch_log, args=(app,), daemon=True)
    t.start()
