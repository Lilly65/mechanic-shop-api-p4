from mechanic_shop import ma, db
from mechanic_shop.models.schemas import Customer
from marshmallow import fields

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        sqla_session = db.session

class LoginSchema(ma.Schema):
    email    = fields.String(required=True)
    password = fields.String(required=True)

customer_schema  = CustomerSchema()
customers_schema = CustomerSchema(many=True)
login_schema     = LoginSchema()