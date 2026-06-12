from flask import Blueprint

customers_bp = Blueprint('customers', __name__, url_prefix='/customers')

from mechanic_shop.blueprints.customers import routes