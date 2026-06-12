from mechanic_shop import ma, db
from mechanic_shop.models.schemas import Mechanic

class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        sqla_session = db.session

mechanic_schema  = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)