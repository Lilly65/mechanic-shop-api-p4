from flask import Blueprint

mechanics_bp = Blueprint('mechanics', __name__, url_prefix='/mechanics')

from mechanic_shop.blueprints.mechanics import routes