from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flasgger import Swagger

db = SQLAlchemy()
ma = Marshmallow()
limiter = Limiter(key_func=get_remote_address)
cache = Cache()

# Swagger template defines the overall API info and security definitions.
# The Bearer security definition enables the Authorize button in the Swagger UI,
# allowing token-protected routes to be tested directly from the docs page.
swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Mechanic Shop API",
        "description": "API for managing customers, mechanics, service tickets, and inventory.",
        "version": "1.0"
    },
    # host is the base URL of the live API with no protocol prefix.
    # schemes tells Swagger to send its requests over https, which Render requires.
    "host": "mechanic-shop-api-p4.onrender.com",
    "schemes": ["https"],
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT token. Enter in the format: Bearer <token>"
        }
    }
}

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}

def create_app(config=None):
    app = Flask(__name__)

    # Apply the provided config class, defaulting to development when none is given.
    # from_object reads every uppercase attribute from the class into app.config.
    if config:
        app.config.from_object(config)
    else:
        app.config.from_object('config.DevelopmentConfig')

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)
    Swagger(app, template=swagger_template, config=swagger_config)

    from mechanic_shop.blueprints.customers import customers_bp
    from mechanic_shop.blueprints.mechanics import mechanics_bp
    from mechanic_shop.blueprints.service_tickets import service_tickets_bp
    from mechanic_shop.blueprints.inventory import inventory_bp

    app.register_blueprint(customers_bp)
    app.register_blueprint(mechanics_bp)
    app.register_blueprint(service_tickets_bp)
    app.register_blueprint(inventory_bp)

    return app