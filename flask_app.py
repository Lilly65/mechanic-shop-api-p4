from mechanic_shop import create_app
from mechanic_shop import db

# Production config reads the database URI and secret key from environment
# variables supplied by Render.
app = create_app('config.ProductionConfig')

with app.app_context():
    db.create_all()